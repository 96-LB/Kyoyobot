import random, discord
from discord import app_commands as slash, Message, Client
from functools import wraps
from typing import Callable, Any, Awaitable, List, Dict, Protocol, TypeVar
from util.debug import DEBUG_GUILD, error
from util.settings import Config

DEBUG = True

class Trigger(Protocol):
    async def __call__(self, bot: Client, message: Message) -> None: ...

def after_trigger(pretrigger: Trigger):
    def wrapper(trigger: Trigger):
        @wraps(trigger)
        async def wrapped(bot: Client, message: Message):
            try:
                await pretrigger(bot, message)
            except Exception as e:
                error(e, f'Failed to execute trigger {pretrigger}')
            try:
                await trigger(bot, message)
            except Exception as e:
                error(e, f'Failed to execute trigger {trigger}!')
        return wrapped
    return wrapper

def if_keyword(keyword: str):
    def wrapper(trigger: Trigger):
        @wraps(trigger)
        async def wrapped(bot: Client, message: Message):
            if keyword in message.content:
                await trigger(bot, message)
        return wrapped
    return wrapper

def with_probability(probability: float):
    def wrapper(trigger: Trigger):
        @wraps(trigger)
        async def wrapped(bot: Client, message: Message):
            if random.random() <= probability:
                await trigger(bot, message)
        return wrapped
    return wrapper

def action_send_response(response: str):
    def wrapper(trigger: Trigger):
        @wraps(trigger)
        async def wrapped(bot: Client, message: Message) -> None:
            await message.channel.send(response)
        return wrapped
    return wrapper

def action_react_custom(emoji_id: int):
    def wrapper(trigger: Trigger):
        @wraps(trigger)
        async def wrapped(bot: Client, message: Message) -> None:
            await message.add_reaction(bot.get_emoji(emoji_id))
        return wrapped
    return wrapper
    
def action_react_standard(emoji: str):
    def wrapper(trigger: Trigger):
        @wraps(trigger)
        async def wrapped(bot: Client, message: Message) -> None:
            await message.add_reaction(emoji)
        return wrapped
    return wrapper


### JASON TRIGGERS ###

jason_trigger_types = {}

def jason_trigger(name: str):
    def wrapper(factory: Callable[..., Trigger]):
        jason_trigger_types[name] = factory
        return factory
    return wrapper

@jason_trigger('keyword_response')
def trigger_response(*, keyword: str, probability: float, response: str, **kwargs: Any) -> Trigger:
    @if_keyword(keyword)
    @with_probability(probability)
    @action_send_response(response)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger('keyword_reaction_standard')
def trigger_reaction_standard(*, keyword: str, probability: float, emoji: str,  **kwargs: Any) -> Trigger:
    @if_keyword(keyword)
    @with_probability(probability)
    @action_react_standard(emoji)
    async def trigger(bot: Client, message: Message): ...
    return trigger

@jason_trigger('keyword_reaction_custom')
def trigger_reaction_custom(*, keyword: str, probability: float, emoji_id: int, **kwargs: Any) -> Trigger:
    @if_keyword(keyword)
    @with_probability(probability)
    @action_react_custom(emoji_id)
    async def trigger(bot: Client, message: Message): ...
    return trigger

### SETUP ###

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    async def trigger(bot: Client, message: Message): ...

    trigger_config : List[Dict[str, Any]] = Config.get('triggers', [])

    for trigger_info in trigger_config:
        trigger_type = trigger_info.get('type')
        trigger_factory = jason_trigger_types.get(trigger_type)
        
        try:
            new_trigger = trigger_factory(**trigger_info)
        except TypeError as e:
            error(e, f'Failed to create sticker of type {trigger_type}!')
            continue
            
        trigger = after_trigger(trigger)(new_trigger)
    
    @bot.event
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot (prevents potential infinite loops)
        if message.author == bot.user:
            return
        
        if not DEBUG or (message.guild is not None and message.guild.id == DEBUG_GUILD.id): #todo: change this
            await trigger(bot, message)