from util.settings import TalkConfig
import random

class START: ...
class END: ...

WORD_TYPE = str | START | END

class WordData:
    '''Used by TalkGenerator to store data about word mappings.'''

    def __init__(self, words: list[WORD_TYPE], counts: list[int]) -> None:
        '''Initializes WordData. Raises ValueError if words and counts aren't
        the same length.'''
        
        if len(words) != len(counts):
            raise ValueError("WordData :: words and counts must be of the same length.")

        self.words = words
        self.counts = counts

    def choose_word(self) -> WORD_TYPE:
        '''Chooses a random word that will be the next word in the text.'''

        ret = random.choices(self.words, weights=self.counts)
        return ret[0]

class TalkGenerator:
    '''Handles generating text that sounds like Kyoyo.'''

    word_to_data: dict[WORD_TYPE, WordData] = {}

    @classmethod
    def setup(cls) -> None:
        '''Sets up word_to_data using the configuration loaded by TalkConfig.'''

        for from_word in TalkConfig.keys():
            words_and_counts: list[tuple[str, int]] = [(word if word else END, int(count)) \
                for (word, count) in TalkConfig.get(from_word).get('next_words').items()]
            TalkGenerator.word_to_data[from_word if from_word else START] = WordData(
                words=[word for (word, _) in words_and_counts],
                counts=[count for (_, count) in words_and_counts],
            )

    @classmethod
    def generate(cls) -> str:
        '''Generates text using the loaded data.'''

        words: list[str] = []
        current_word: WORD_TYPE = START

        while current_word is not END:
            next_word_data: WordData | None = TalkGenerator.word_to_data.get(current_word)
            if not next_word_data:
                raise RuntimeError(f'TalkGenerator.generate() :: {current_word} has no data associated with it.')
            
            next_word: WORD_TYPE = next_word_data.choose_word()
            if isinstance(next_word, str):
                words.append(next_word)
            current_word = next_word

        return ' '.join(words)