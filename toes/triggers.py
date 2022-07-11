import random, re
from discord import app_commands as slash, Client, Message
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Optional, Sequence
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
async def with_probability(bot: Client, message: Message, *, trigger: Trigger, probability: float, **kwargs: Any) -> None:
    '''Executes the trigger with a random probability.'''
    
    if random.random() * 100 <= probability:
        await trigger(bot, message)

@modifier
async def action_trigger(bot: Client, message: Message, trigger: Trigger, *, other: Trigger, **kwargs: Any) -> None:
    '''Executes another trigger.'''
    
    await other(bot, message)
    await trigger(bot, message)

@modifier
async def action_send_response(bot: Client, message: Message, trigger: Trigger, *, response: str, **kwargs: Any) -> None:
    '''Sends a text response in the channel in which the message was received.'''
    
    with catch(Exception, 'Triggers :: Failed to send message!'):
        await message.channel.send(response)
    
    await trigger(bot, message)

@modifier
async def action_react_standard(bot: Client, message: Message, trigger: Trigger, *, emoji: str, **kwargs: Any) -> None:
    '''Reacts to the message with a standard emoji.'''
    
    with catch(Exception, f'Triggers :: Failed to add standard emoji reaction "{emoji}"!'):
        await message.add_reaction(emoji)
    
    await trigger(bot, message)

@modifier
async def action_react_custom(bot: Client, message: Message, trigger: Trigger, *, emoji_id: int, **kwargs: Any) -> None:
    '''Reacts to the message with a custom emoji.'''
    
    with catch(Exception, f'Triggers :: Failed to add custom emoji reaction "{emoji_id}"!'):
        await message.add_reaction(bot.get_emoji(emoji_id)) # type: ignore
    
    await trigger(bot, message)

###

@modifier
async def pick_random(bot: Client, message: Message, trigger: Trigger, *, factory: TriggerModifierFactory, args: Sequence, **kwargs: Any):
    '''Applies a random argument from the list to the provided modifier factory.'''

    # placeholder definition in case of exception 
    async def modified(bot: Client, message: Message) -> None: ...
    
    with catch(Exception, f'Triggers :: Failed to execute random trigger {factory}!'):
        modifier : TriggerModifier = factory(random.choice(args))
        modified : Trigger = modifier(trigger) # type: ignore[no-redef]

    await modified(bot, message)
    
### JASON TRIGGERS ###

jason_trigger_types = {}

def jason_trigger(factory: TriggerFactory, name: str = None) -> TriggerFactory:
    '''Allows a trigger factor to be accessed from the configuration file.'''

    # logs the factory function in the dictionary with the specified name
    if name is None:
        name = factory.__name__
        if name.startswith('trigger_'): # common prefix
            name = name[8:]
    jason_trigger_types[name] = factory
    
    return factory

###

@jason_trigger
def trigger_keyword_response(*, keyword: str, case_sensitive: bool = False, probability: float = 100, response: str, **kwargs: Any) -> Trigger:
    '''Triggers a text response upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @action_send_response(response)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger
def trigger_keyword_random_response(*, keyword: str, case_sensitive: bool = False, probability: float = 100, responses: Sequence[str], **kwargs: Any) -> Trigger:
    '''Triggers a random text response upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @pick_random(action_send_response, responses)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger
def trigger_keyword_reaction_standard(*, keyword: str, case_sensitive: bool = False, probability: float = 100, emoji: str,  **kwargs: Any) -> Trigger:
    '''Triggers a standard emoji reaction upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @action_react_standard(emoji)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger
def trigger_keyword_reaction_custom(*, keyword: str, case_sensitive: bool = False, probability: float = 100, emoji_id: int, **kwargs: Any) -> Trigger:
    '''Triggers a custom emoji reaction upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @action_react_custom(emoji_id)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger
def trigger_keyword_reaction_random(*, keyword: str, case_sensitive: bool = False, probability: float = 100, emojis: Sequence[str],  **kwargs: Any) -> Trigger:
    '''Triggers a standard emoji reaction upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @pick_random(action_react_standard, emojis)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger
def trigger_user_response(*, author_id: int, probability: float = 100, response: str,  **kwargs: Any) -> Trigger:
    '''Triggers a text response upon detecting an author.'''
   
    @if_author(author_id)
    @with_probability(probability)
    @action_send_response(response)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger
def trigger_user_reaction_standard(*, author_id: int, probability: float = 100, emoji: str,  **kwargs: Any) -> Trigger:
    '''Triggers a custom emoji reaction upon detecting an author.'''
   
    @if_author(author_id)
    @with_probability(probability)
    @action_react_standard(emoji)
    async def trigger(bot: Client, message: Message): ...
    return trigger
 
@jason_trigger
def trigger_user_reaction_custom(*, author_id: int, probability: float = 100, emoji_id: int, **kwargs: Any) -> Trigger:
    '''Triggers a custom emoji reaction upon detecting an author.'''
   
    @if_author(author_id)
    @with_probability(probability)
    @action_react_custom(emoji_id)
    async def trigger(bot: Client, message: Message): ...
    return trigger

###

async def trigger_null(bot: Client, message: Message, /) -> None: ...

def create_trigger(types : Sequence[str], **kwargs) -> Optional[Trigger]:
    '''Creates a trigger by stacking the specified modifier types.'''
    
    trigger = trigger_null
    
    for type in reversed(types):
        try:
            modifier_factory = modifiers.get(type)
            modifier = modifier_factory(**kwargs) # type: ignore
            trigger = modifier(trigger) # type: ignore
        except TypeError as e:
            error(e, f'Triggers :: Failed to create trigger of type {types} because of type {type}.')
            return None        

    return trigger

def combine_triggers(first: Trigger, second: Trigger) -> Trigger:
    return action_trigger(other=first)(second)
    
### SETUP ###

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    trigger = trigger_null

    # pulls trigger information from the configuration file
    trigger_config = []
    with catch(TypeError, 'Triggers :: Failed to load trigger configuration!'):
        trigger_config = list(Config.get('triggers')) # type: ignore

    for trigger_info in trigger_config:
        trigger_type = trigger_info.get('type', '').split()
        new_trigger: Optional[Trigger] = create_trigger(trigger_type, **trigger_info)
        
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
