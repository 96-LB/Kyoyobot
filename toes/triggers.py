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


class Trigger:
    '''Provides generic functionality for triggers.'''

    def __init__(self, response_handler: Callable[[Client, Message], Awaitable[None]]) -> None:
        '''Creates a generic Trigger instance.'''

        self._response_handler = response_handler

    async def process_message(self, bot: Client, message: Message) -> None:
        '''Processes messages fed in from on_message() event.'''

        await self._response_handler(bot, message)


T = TypeVar('T', bound='KeywordTrigger')
class KeywordTrigger(Trigger):
    '''Specific type of Trigger that triggers when a keyword is present in a
    message.'''

    def __init__(self, keyword: str, response_handler: Callable[[Message], Awaitable[None]], probability: float):
        '''Creates a generic KeywordTrigger with the generic response_handler.'''

        super().__init__(if_keyword(keyword)(with_probability(probability)(response_handler))) 

    @classmethod
    def from_phrase_response(cls, keyword: str, phrase_response: str, probability: float) -> T: 
        '''Creates a simple KeywordTrigger that sends a message with the given phrase.'''

        return cls(keyword, trigger_send_response(phrase_response), probability)

    @classmethod
    def from_reaction_response(cls, keyword: str, emoji_name: str, is_custom_emoji: bool, probability: float) -> T:
        '''Creates a simple KeywordTrigger that reacts to the triggering message
        with the given emoji.

        :param str emoji: either a Unicode emoji or custom emoji name, depending
            on parameter is_custom_emoji
        '''


        return cls(keyword, (lambda x, y: '') if is_custom_emoji else trigger_reaction_standard(emoji_name), probability)

class TriggerManager:
    '''Stores and manages all trigger instances.'''

    _triggers: List[Trigger] = []

    @classmethod
    def load_from_config(cls) -> None:
        '''Loads all triggers from config.'''

        TriggerManager._load_keyword_phrase_response_triggers_from_config()
        TriggerManager._load_keyword_reaction_response_triggers_from_config()

    @classmethod
    def _load_keyword_phrase_response_triggers_from_config(cls) -> None:
        '''Loads keyword_phrase_response triggers from config and adds them.'''

        triggers: Dict = Config.get('triggers')
        keyword_phrase_response_triggers = triggers.get('keyword_phrase_response', [])
        for trigger_info in keyword_phrase_response_triggers:
            TriggerManager.add_trigger(KeywordTrigger.from_phrase_response(**trigger_info))

    @classmethod
    def _load_keyword_reaction_response_triggers_from_config(cls) -> None:
        '''Loads keyword_reaction_response triggers from config and adds them.'''

        triggers: Dict = Config.get('triggers')
        keyword_reaction_response_triggers = triggers.get('keyword_reaction_response', [])
        for trigger_info in keyword_reaction_response_triggers:
            TriggerManager.add_trigger(KeywordTrigger.from_reaction_response(**trigger_info))

    @classmethod
    def add_trigger(cls, trigger: Trigger) -> None:
        '''Adds a trigger.'''

        TriggerManager._triggers.append(trigger)

    @classmethod
    async def process_message_all(cls, bot: Client, message: Message) -> None:
        '''Processes all triggers.'''

        for trigger in TriggerManager._triggers:
            await trigger.process_message(bot, message)

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    TriggerManager.load_from_config()
    
    @bot.event
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot (prevents potential infinite loops)
        if message.author == bot.user:
            return
        if not DEBUG or message.guild.id == DEBUG_GUILD.id: #todo: change this
            await TriggerManager.process_message_all(bot, message)