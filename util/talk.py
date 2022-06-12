from typing import cast, Dict, List, Tuple
from util.settings import TalkConfig
import random

class WordData:
    '''Used by TalkGenerator to store data about word mappings.'''

    def __init__(self, words: List[str], counts: List[int]) -> None:
        '''Initializes WordData. Raises ValueError if words and counts aren't
        the same length.'''
        
        if len(words) != len(counts):
            raise ValueError("WordData :: words and counts must be of the same length.")

        self.words = words
        self.counts = counts

    def choose_word(self) -> str:
        '''Chooses a random word that will be the next word in the text.'''

        ret = random.choices(self.words, weights=self.counts)
        return ret[0]

class TalkGenerator:
    '''Handles generating text that sounds like Kyoyo.'''

    word_to_data: Dict[str, WordData] = {}

    @classmethod
    def setup(cls) -> None:
        '''Sets up word_to_data using the configuration loaded by TalkConfig.'''

        for from_word in TalkConfig.keys():
            data = cast(Dict[str, Dict[str, int]], TalkConfig.get(from_word)).get('next_words')
            assert data is not None
            words_and_counts: List[Tuple[str, int]] = [(word, int(count)) \
                for (word, count) in data.items()]
            TalkGenerator.word_to_data[from_word] = WordData(
                words=[word for (word, _) in words_and_counts],
                counts=[count for (_, count) in words_and_counts],
            )

    @classmethod
    def generate(cls) -> str:
        '''Generates text using the loaded data.'''

        words: List[str] = []
        word: str = TalkGenerator.word_to_data[''].choose_word()

        while word:
            words.append(word)
            word = TalkGenerator.word_to_data[word].choose_word()

        return ' '.join(words)