import random, discord
from discord import app_commands as slash, Message, Client
from functools import wraps
from typing import Callable, Any, Awaitable, List, Dict, Protocol, TypeVar
from util.debug import DEBUG_GUILD, error
from util.settings import Config

DEBUG = True

class Trigger(Protocol):
    async def __call__(self, bot: Client, message: Message) -> None: ...

def modifier(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        def wrapper(trigger: Trigger):
            @wraps(trigger)
            async def wrapped2(bot: Client, message: Message):
                await f(bot, message, trigger, *args, **kwargs)
            return wrapped2
        return wrapper
    return wrapped

@modifier
async def if_keyword(bot: Client, message: Message, trigger: Trigger, keyword: str):
    if keyword in message.content:
        await trigger(bot, message)

@modifier
async def with_probability(bot: Client, message: Message, trigger: Trigger, probability: float):
    if random.random() <= probability:
        await trigger(bot, message)

@modifier
async def action_trigger(bot: Client, message: Message, trigger: Trigger, other: Trigger):
    await other(bot, message)
    await trigger(bot, message)

@modifier
async def action_send_response(bot: Client, message: Message, trigger: Trigger, response: str):
    try:
        await message.channel.send(response)
    except Exception as e:
        error(e, 'Triggers :: Failed to send message!')
    await trigger(bot, message)

@modifier
async def action_react_custom(bot: Client, message: Message, trigger: Trigger, emoji_id: int):
    try:
        await message.add_reaction(bot.get_emoji(emoji_id))
    except Exception as e:
        error(e, 'Triggers :: Failed to add custom emoji reaction!')
    await trigger(bot, message)

@modifier
async def action_react_standard(bot: Client, message: Message, trigger: Trigger, emoji: str):
    try:
        await message.add_reaction(emoji)
    except Exception as e:
        error(e, 'Triggers :: Failed to add standard emoji reaction!')
    await trigger(bot, message)
    

### JASON TRIGGERS ###

jason_trigger_types = {}

def jason_trigger(name: str):
    def wrapper(factory: Callable[..., Trigger]):
        jason_trigger_types[name] = factory
        return factory
    return wrapper

###

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

        #combines the triggers
        trigger = action_trigger(trigger)(new_trigger)
    
    @bot.event
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot (prevents potential infinite loops)
        if message.author == bot.user:
            return
        
        if not DEBUG or (message.guild is not None and message.guild.id == DEBUG_GUILD.id): #todo: change this
            await trigger(bot, message)