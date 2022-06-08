import random, discord
from discord import app_commands as slash, Message, Client
from functools import wraps
from typing import Callable, Any, Awaitable, List, Dict, Protocol, TypeVar
from util.debug import DEBUG_GUILD
from util.settings import Config

DEBUG = True

class Trigger(Protocol):
    async def __call__(self, bot: Client, message: Message) -> None: ...


def after_trigger(pretrigger: Trigger):
    def wrapper(trigger: Trigger):
        @wraps(trigger)
        async def wrapped(bot: Client, message: Message):
            await pretrigger(bot, message)
            await trigger(bot, message)
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

def trigger_send_response(response: str) -> Trigger:
    async def trigger(bot: Client, message: Message) -> None:
        await message.channel.send(response)
    return trigger

def trigger_reaction_custom(emoji_id: int) -> Trigger:
    async def trigger(bot: Client, message: Message) -> None:
        await message.add_reaction(bot.get_emoji(emoji_id))
    return trigger
    
def trigger_reaction_standard(emoji: str) -> Trigger:
    async def trigger(bot: Client, message: Message) -> None:
        await message.add_reaction(emoji)
    return trigger

def trigger_null() -> Trigger:
    async def trigger(bot: Client, message: Message) -> None:
        pass
    return trigger


class KeywordTrigger():
    '''Specific type of Trigger that triggers when a keyword is present in a
    message.'''

    @classmethod
    def from_phrase_response(cls, keyword: str, phrase_response: str, probability: float) -> Trigger:
        '''Creates a simple KeywordTrigger that sends a message with the given phrase.'''

        return if_keyword(keyword)(with_probability(probability)(trigger_send_response(phrase_response)))

    @classmethod
    def from_reaction_response(cls, keyword: str, emoji_name: str, is_custom_emoji: bool, probability: float) -> Trigger:
        '''Creates a simple KeywordTrigger that reacts to the triggering message
        with the given emoji.

        :param str emoji: either a Unicode emoji or custom emoji name, depending
            on parameter is_custom_emoji
        '''

        return if_keyword(keyword)(with_probability(probability)((lambda x, y: '') if is_custom_emoji else trigger_reaction_standard(emoji_name)))



def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    trigger: Trigger = trigger_null()

    trigger_config : Dict[str, str] = Config.get('triggers')

    keyword_phrase_response_triggers = trigger_config.get('keyword_phrase_response', [])
    for trigger_info in keyword_phrase_response_triggers:
        trigger = after_trigger(trigger)(KeywordTrigger.from_phrase_response(**trigger_info))

    keyword_reaction_response_triggers = trigger_config.get('keyword_reaction_response', [])
    for trigger_info in keyword_reaction_response_triggers:
        trigger = after_trigger(trigger)(KeywordTrigger.from_reaction_response(**trigger_info))

    
    @bot.event
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot (prevents potential infinite loops)
        if message.author == bot.user:
            return
        
        if not DEBUG or (message.guild is not None and message.guild.id == DEBUG_GUILD.id): #todo: change this
            await trigger(bot, message)