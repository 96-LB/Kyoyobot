import random
from discord import app_commands as slash, Message, Client
from typing import Callable, Awaitable, List, Dict, TypeVar
from util.debug import DEBUG_GUILD
from util.settings import Config

DEBUG = True

class Trigger:
    '''Provides generic functionality for triggers.'''

    def __init__(self, filter_handler: Callable[[Message], Awaitable[bool]], \
        response_handler: Callable[[Message], Awaitable[None]], probability: float) -> None:
        '''Creates a generic Trigger instance.'''

        # Validate probability (must be in the range [0.0, 1.0])
        if probability < 0.0 or probability > 1.0:
            raise ValueError(f'Probability {probability} for trigger is invalid: must be in the range [0.0, 1.0].')

        self._filter_handler = filter_handler
        self._response_handler = response_handler
        self._probability = probability

    async def process_message(self, message: Message) -> None:
        '''Processes messages fed in from on_message() event.'''

        if await self._filter_handler(message):
            if random.random() <= self._probability:
                await self._response_handler(message)


T = TypeVar('T', bound='KeywordTrigger')
class KeywordTrigger(Trigger):
    '''Specific type of Trigger that triggers when a keyword is present in a
    message.'''

    def __init__(self, keyword: str, response_handler: Callable[[Message], Awaitable[None]], probability: float):
        '''Creates a generic KeywordTrigger with the generic response_handler.'''

        self.keyword = keyword

        def generate_filter_handler():
            async def _(message: Message):
                return keyword in message.content
            return _
        super().__init__(generate_filter_handler(), response_handler, probability) 

    @classmethod
    def from_phrase_response(cls, keyword: str, phrase_response: str, probability: float) -> T: 
        '''Creates a simple KeywordTrigger that sends a message with the given phrase.'''

        def generate_response_handler():
            async def _(message: Message):
                await message.channel.send(phrase_response)
            return _
        return cls(keyword, generate_response_handler(), probability)

    @classmethod
    def from_reaction_response(cls, keyword: str, emoji_name: str, is_custom_emoji: bool, probability: float) -> T:
        '''Creates a simple KeywordTrigger that reacts to the triggering message
        with the given emoji.

        :param str emoji: either a Unicode emoji or custom emoji name, depending
            on parameter is_custom_emoji
        '''

        def generate_response_handler():
            async def _(message: Message):
                if is_custom_emoji:
                    emoji = discord.utils.get(message.guild.emojis, name=emoji_name)
                else:
                    emoji = emoji_name
                await message.add_reaction(emoji)
            return _
        return cls(keyword, generate_response_handler(), probability)

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
    async def process_message_all(cls, message: Message) -> None:
        '''Processes all triggers.'''

        for trigger in TriggerManager._triggers:
            await trigger.process_message(message)

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''
    
    @bot.event
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot (prevents potential infinite loops)
        if message.author == bot.user:
            return
        if not DEBUG or message.guild.id == DEBUG_GUILD.id: #todo: change this
            await TriggerManager.process_message_all(message)