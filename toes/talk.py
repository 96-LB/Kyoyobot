import random
from discord import app_commands as slash, Client, Interaction
from typing import cast, Dict, Iterator, List, Tuple
from util.debug import DEBUG_GUILD
from util.settings import TalkConfig

DEBUG = False

class TalkGenerator:
    '''Handles generating text that sounds like Kyoyo.'''

    word_to_data: Dict[str, Tuple[Iterator[str], Iterator[int]]] = {}

    @classmethod
    def setup(cls) -> None:
        '''Sets up word_to_data using the configuration loaded by TalkConfig.'''

        for word in TalkConfig.keys():
            data = cast(Dict[str, Dict[str, int]], TalkConfig[word])['next_words']         
            cls.word_to_data[word] = tuple(zip(*data.items()))

    @classmethod
    def choose_word(cls, word: str) -> str:
        '''Chooses a random word that will be the next word in the text.'''

        words, counts = cls.word_to_data.get(word)
        return random.choices(words, weights=counts)[0]
    
    @classmethod
    def generate(cls) -> str:
        '''Generates text using the loaded data.'''

        words: List[str] = []
        word: str = cls.choose_word('')

        while word:
            words.append(word)
            word = cls.choose_word(word)

        return ' '.join(words)

@slash.command()
async def talk(interaction: Interaction) -> None:
    '''Talk to your one true friend, Kyoyobot.'''

    await interaction.response.send_message(TalkGenerator.generate())

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    TalkGenerator.setup()
    tree.add_command(talk, guild=(DEBUG_GUILD if DEBUG else None))