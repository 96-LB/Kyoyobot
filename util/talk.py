from typing import cast, Dict, Iterator, List, Tuple
from util.settings import TalkConfig
import random

class TalkGenerator:
    '''Handles generating text that sounds like Kyoyo.'''

    word_to_data: Dict[str, Tuple[Iterator[str], Iterator[int]]] = {}

    @classmethod
    def setup(cls) -> None:
        '''Sets up word_to_data using the configuration loaded by TalkConfig.'''

        for word in TalkConfig.keys():
            data = cast(Dict[str, Dict[str, int]], cls[word])['next_words']         
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
        word: str = TalkGenerator.word_to_data[''].choose_word()

        while word:
            words.append(word)
            word = TalkGenerator.word_to_data[word].choose_word()

        return ' '.join(words)