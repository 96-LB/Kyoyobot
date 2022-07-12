import random, re
from discord import app_commands as slash, Client, Message
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Mapping, Optional, Sequence
from util.debug import DEBUG_GUILD, catch, error
from util.settings import Config

DEBUG = True

Trigger = Callable[[Client, Message], Coroutine[Any, Any, None]]
TriggerFactory = Callable[..., Trigger]
TriggerModifier = Callable[[Trigger], Trigger]
TriggerModifierFactory = Callable[..., TriggerModifier]

### MODIFIERS ###

modifiers = {}

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

@modifier
async def do_another(bot: Client, message: Message, trigger: Trigger, *, other: Trigger, **kwargs: Any) -> None:
    '''Executes another trigger before this one.'''
    
    await other(bot, message)
    await trigger(bot, message)

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
        await message.add_reaction(bot.get_emoji(emoji_id)) # type: ignore
    
    await trigger(bot, message)

###

@modifier
async def do_random(bot: Client, message: Message, trigger: Trigger, *, r_type: str, r_args: Mapping[str, Sequence], **kwargs: Any):
    '''Applies a random argument from the list to the provided modifier factory.'''

    # placeholder definition in case of exception 
    modified = null_trigger
    
    with catch(Exception, f'Triggers :: Failed to execute random trigger of type {r_type} with args {r_args}!'):
        factory: TriggerModifierFactory = modifiers[r_type]
        modifier: TriggerModifier = factory(**{key: random.choice(values) for key, values in r_args.items()})
        modified = modifier(trigger)

    await modified(bot, message)

###

async def null_trigger(bot: Client, message: Message, /) -> None: ...

def create_trigger(**kwargs) -> Optional[Trigger]:
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
            modifier_factory = modifiers.get(type)
            modifier = modifier_factory(**kwargs) # type: ignore
            trigger = modifier(trigger)
        except TypeError as e:
            error(e, f'Triggers :: Failed to create trigger of type {types} because of type "{type}".')
            return None

    return trigger

def combine_triggers(first: Trigger, second: Trigger) -> Trigger:
    return do_another(other=first)(second)
    
### SETUP ###

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    trigger = null_trigger

    # pulls trigger information from the configuration file
    trigger_config = []
    with catch(TypeError, 'Triggers :: Failed to load trigger configuration!'):
        trigger_config = list(Config.get('triggers')) # type: ignore

    for trigger_info in trigger_config:
        new_trigger: Optional[Trigger] = create_trigger(**trigger_info)
        
        # combines the triggers
        if new_trigger is not None:
            trigger = combine_triggers(trigger, new_trigger)
    
    @bot.event
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot to prevent infinite loops
        if message.author == bot.user:
            return
        
        # execute the master trigger if not in debug mode
        if not DEBUG or (message.guild is not None and message.guild.id == DEBUG_GUILD.id):
            await trigger(bot, message)
