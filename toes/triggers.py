import random, re
from discord import app_commands as slash, Message, Client
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Sequence
from util.debug import DEBUG_GUILD, error
from util.settings import Config

DEBUG = True

Trigger = Callable[[Client, Message], Coroutine[Any, Any, None]]
TriggerFactory = Callable[..., Trigger]
TriggerModifier = Callable[[Trigger], Trigger]
TriggerModifierFactory = Callable[..., TriggerModifier]

### MODIFIERS ###

def modifier(func: Callable[..., Awaitable[None]]) -> TriggerModifierFactory:
    '''Converts a flat trigger modifier into a compositable decorator factory.'''
    
    @wraps(func)
    def decorator_wrapper(*args: Any, **kwargs: Any) -> TriggerModifier:
        #a factory function which produces a decorator
        def decorator(trigger: Trigger) -> Trigger:
            #a decorator function
            @wraps(trigger)
            async def wrapper(bot: Client, message: Message) -> None:
                #a wrapper which passes in the environment to the original function
                await func(bot, message, trigger, *args)
            return wrapper
        return decorator
    return decorator_wrapper

###

# IMPORTANT!
# @modifier changes the function signature of each of the following functions
# to call them, do NOT use `await`, and omit the first three arguments 

@modifier
async def if_keyword(bot: Client, message: Message, trigger: Trigger, keyword: str, case_sensitive: bool = False) -> None:
    '''Executes the trigger only if the keyword is present in the message.'''
    
    if re.search(keyword, message.content, re.IGNORECASE if not case_sensitive else 0):
        await trigger(bot, message)

@modifier
async def if_author(bot: Client, message: Message, trigger: Trigger, author_id: int) -> None:
    '''Executes the trigger only if the provided ID matches the message author.'''
   
    if message.author.id == author_id:
        await trigger(bot, message)

@modifier
async def with_probability(bot: Client, message: Message, trigger: Trigger, probability: float) -> None:
    '''Executes the trigger with a random probability.'''
    
    if random.random() * 100 <= probability:
        await trigger(bot, message)

@modifier
async def action_trigger(bot: Client, message: Message, trigger: Trigger, other: Trigger) -> None:
    '''Executes another trigger.'''
    
    await other(bot, message)
    await trigger(bot, message)

@modifier
async def action_send_response(bot: Client, message: Message, trigger: Trigger, response: str) -> None:
    '''Sends a text response in the channel in which the message was received.'''
    
    try:
        await message.channel.send(response)
    except Exception as e:
        error(e, 'Triggers :: Failed to send message!')
    
    await trigger(bot, message)

@modifier
async def action_react_standard(bot: Client, message: Message, trigger: Trigger, emoji: str) -> None:
    '''Reacts to the message with a standard emoji.'''
    
    try:
        await message.add_reaction(emoji)
    except Exception as e:
        error(e, 'Triggers :: Failed to add standard emoji reaction!')
    
    await trigger(bot, message)

@modifier
async def action_react_custom(bot: Client, message: Message, trigger: Trigger, emoji_id: int) -> None:
    '''Reacts to the message with a custom emoji.'''
    
    try:
        await message.add_reaction(bot.get_emoji(emoji_id))
    except Exception as e:
        error(e, 'Triggers :: Failed to add custom emoji reaction!')
    
    await trigger(bot, message)

###

@modifier
async def pick_random(bot: Client, message: Message, trigger: Trigger, factory: TriggerModifierFactory, args: Sequence):
    '''Applies a random argument from the list to the provided modifier factory.'''

    try:
        modifier : TriggerModifier = factory(random.choice(args))
        modified : Trigger = modifier(trigger)
    except Exception as e:
        error(e, f'Triggers :: Failed to execute random trigger {factory}!')
        return

    await modified(bot, message)
    
### JASON TRIGGERS ###

jason_trigger_types = {}

def jason_trigger(name: str) -> Callable[[TriggerFactory], TriggerFactory]:
    '''Labels a trigger factory with a string representation.'''
    
    def wrapper(factory: TriggerFactory) -> TriggerFactory:
        jason_trigger_types[name] = factory
        factory.__name__ = f'trigger_{name}'
        return factory
    return wrapper

###

@jason_trigger('keyword_response')
def _(*, keyword: str, case_sensitive: bool = False, probability: float = 100, response: str, **kwargs: Any) -> Trigger:
    '''Triggers a text response upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @action_send_response(response)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger('keyword_random_response')
def _(*, keyword: str, case_sensitive: bool = False, probability: float = 100, responses: Sequence[str], **kwargs: Any) -> Trigger:
    '''Triggers a random text response upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @pick_random(action_send_response, responses)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger('keyword_reaction_standard')
def _(*, keyword: str, case_sensitive: bool = False, probability: float = 100, emoji: str,  **kwargs: Any) -> Trigger:
    '''Triggers a standard emoji reaction upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @action_react_standard(emoji)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger('keyword_reaction_custom')
def _(*, keyword: str, case_sensitive: bool = False, probability: float = 100, emoji_id: int, **kwargs: Any) -> Trigger:
    '''Triggers a custom emoji reaction upon detecting a keyword.'''
    
    @if_keyword(keyword, case_sensitive)
    @with_probability(probability)
    @action_react_custom(emoji_id)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger('user_response')
def _(*, author_id: int, probability: float = 100, response: str,  **kwargs: Any) -> Trigger:
    '''Triggers a text response upon detecting an author.'''
   
    @if_author(author_id)
    @with_probability(probability)
    @action_send_response(response)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger('user_reaction_standard')
def _(*, author_id: int, probability: float = 100, emoji: str,  **kwargs: Any) -> Trigger:
    '''Triggers a custom emoji reaction upon detecting an author.'''
   
    @if_author(author_id)
    @with_probability(probability)
    @action_react_standard(emoji)
    async def trigger(bot: Client, message: Message): ...
    return trigger
 
@jason_trigger('user_reaction_custom')
def _(*, author_id: int, probability: float = 100, emoji_id: int, **kwargs: Any) -> Trigger:
    '''Triggers a custom emoji reaction upon detecting an author.'''
   
    @if_author(author_id)
    @with_probability(probability)
    @action_react_custom(emoji_id)
    async def trigger(bot: Client, message: Message): ...
    return trigger

### SETUP ###

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    async def trigger(__bot: Client, __message: Message) -> None: ...

    # pulls trigger information from the configuration file

    try:
        trigger_config = list(Config.get('triggers')) # type: ignore
    except ValueError as e:
        error(e, 'Triggers :: Failed to load trigger configuration!')
        trigger_config = []

    for trigger_info in trigger_config:
        trigger_type = trigger_info.get('type')
        trigger_factory = jason_trigger_types.get(trigger_type)

        # attempt to create the trigger with the appropriate factory method
        try:
            new_trigger = trigger_factory(**trigger_info) # type: ignore
        except TypeError as e:
            error(e, f'Triggers :: Failed to create trigger of type {trigger_type}!')
            continue

        # combines the triggers
        trigger = action_trigger(trigger)(new_trigger)
    
    @bot.event
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot to prevent infinite loops
        if message.author == bot.user:
            return

        # execute the master trigger if not in debug mode
        if not DEBUG or (message.guild is not None and message.guild.id == DEBUG_GUILD.id):
            await trigger(bot, message)