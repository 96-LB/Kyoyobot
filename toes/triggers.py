import random, re
from discord import app_commands as slash, Client, Message
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Iterable, Mapping, Optional, Sequence, cast

from util.debug import DEBUG, DEBUG_GUILD, catch, error
from util.settings import Config

Trigger = Callable[[Client, Message], Coroutine[Any, Any, None]]
TriggerFactory = Callable[..., Trigger]
TriggerModifier = Callable[[Trigger], Trigger]
TriggerModifierFactory = Callable[..., TriggerModifier]

async def null_trigger(bot: Client, message: Message, /) -> None: ...

### MODIFIERS ###

modifiers: dict[str, TriggerModifierFactory] = {}

def modifier(func: Callable[..., Awaitable[None]]) -> TriggerModifierFactory:
    '''Converts a flat trigger modifier into a compositable decorator factory.'''

    @wraps(func)
    def decorator_wrapper(**kwargs: Any) -> TriggerModifier:
        #a factory function which produces a decorator
        def decorator(trigger: Trigger) -> Trigger:
            #a decorator function
            @wraps(trigger)
            async def wrapper(bot: Client, message: Message) -> None:
                #a wrapper which passes in the environment to the original function
                await func(bot, message, trigger, **kwargs)
            return wrapper
        return decorator

    # logs the modifier so that it is accessible from the jason file
    modifiers[func.__name__] = decorator_wrapper
    return decorator_wrapper

###

# IMPORTANT!
# @modifier changes the function signature of each of the following functions
# to call them, do NOT use `await`, and omit the first three arguments

@modifier
async def if_keyword(bot: Client, message: Message, trigger: Trigger, *, keyword: str, case_sensitive: bool = False, **kwargs: Any) -> None:
    '''Executes the trigger only if the keyword is present in the message.'''
    
    if re.search(keyword, message.content, re.IGNORECASE if not case_sensitive else 0):
        await trigger(bot, message)

@modifier
async def if_author(bot: Client, message: Message, trigger: Trigger, *, author_id: int, **kwargs: Any) -> None:
    '''Executes the trigger only if the provided ID matches the message author.'''
    
    if message.author.id == author_id:
        await trigger(bot, message)

@modifier
async def if_lucky(bot: Client, message: Message, trigger: Trigger, *, probability: float, **kwargs: Any) -> None:
    '''Executes the trigger with a random probability.'''
    
    if random.random() * 100 <= probability:
        await trigger(bot, message)

###

@modifier
async def do_text(bot: Client, message: Message, trigger: Trigger, *, text: str, **kwargs: Any) -> None:
    '''Sends a text response in the channel in which the message was received.'''
    
    with catch(Exception, 'Triggers :: Failed to send message!'):
        await message.channel.send(text)
    
    await trigger(bot, message)

@modifier
async def do_react(bot: Client, message: Message, trigger: Trigger, *, emoji: str, **kwargs: Any) -> None:
    '''Reacts to the message with a standard emoji.'''
    
    with catch(Exception, f'Triggers :: Failed to add standard emoji reaction "{emoji}"!'):
        await message.add_reaction(emoji)
    
    await trigger(bot, message)

@modifier
async def do_react_custom(bot: Client, message: Message, trigger: Trigger, *, emoji_id: int, **kwargs: Any) -> None:
    '''Reacts to the message with a custom emoji.'''
    
    with catch(Exception, f'Triggers :: Failed to add custom emoji reaction "{emoji_id}"!'):
        emoji = bot.get_emoji(emoji_id)
        if emoji:
            await message.add_reaction(emoji)
    
    await trigger(bot, message)

###

@modifier
async def do_another(bot: Client, message: Message, trigger: Trigger, *, other: Mapping[str, Any], **kwargs: Any) -> None:
    '''Executes another trigger before this one.'''
    
    other_trigger = create_trigger(**other)
    if other_trigger is not None:
        await other_trigger(bot, message)
    await trigger(bot, message)

@modifier
async def do_random(bot: Client, message: Message, trigger: Trigger, *, choices: Mapping[str, Sequence[Any]], **kwargs: Any):
    '''Executes another trigger with random arguments before this one.'''
    
    with catch(Exception, f'Triggers :: Failed to execute random trigger!'):
        other = {key: values if key == 'type' else random.choice(values) for key, values in choices.items()}
    
    modified = add_trigger(trigger, other)
    await modified(bot, message)

### SETUP ###

def add_trigger(trigger: Trigger, other: Mapping[str, Any]):
    return do_another(other=other)(trigger)

def create_trigger(**kwargs: Any) -> Optional[Trigger]:
    '''Creates a trigger by stacking the specified modifier types.'''
    
    types = kwargs.get('type', '')
    try:
        types = types.split()
    except AttributeError as e:
        error(e, f'Triggers :: Failed to create trigger of unreadable type {types}.')
        return None
    
    trigger = null_trigger
    for type in reversed(types):
        try:
            modifier_factory = modifiers[type]
            modifier = modifier_factory(**kwargs)
            trigger = modifier(trigger)
        except IndexError as e:
            error(e, f'Triggers :: Failed to create trigger of type {types} because of type "{type}".')
            return None
    
    return trigger

def setup(bot: Client) -> Iterable[slash.Command[Any, ..., Any] | slash.Group]:
    '''Sets up this bot module.'''
    
    trigger = null_trigger
    
    # pulls trigger information from the configuration file
    trigger_config: list[dict[str, Any]] = []
    with catch(TypeError, 'Triggers :: Failed to load trigger configuration!'):
        trigger_config = cast(list[dict[str, Any]], Config.get('triggers'))
    
    for trigger_info in trigger_config:
        # combines the triggers
        trigger = add_trigger(trigger, trigger_info)
    
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot to prevent infinite loops
        if message.author == bot.user:
            return
        
        # if in debug mode, only respond in direct messages or the debug server
        if DEBUG and not (message.guild is None or message.guild.id == DEBUG_GUILD.id):
            return
        
        # execute the master trigger
        await trigger(bot, message)
    bot.event(on_message)
    
    return []
