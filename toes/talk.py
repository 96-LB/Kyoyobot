import random
from discord import app_commands as slash, Client, Interaction
from discord.errors import HTTPException
from discord.app_commands.errors import CommandAlreadyRegistered
from typing import cast, Dict, Iterator, List, Tuple
from util.debug import DEBUG_GUILD, catch
from util.settings import TalkConfig

DEBUG = False

def add_talk_command(group: slash.Group, name: str, description: str = '') -> None:
    '''Generates a talk commmand and adds it to the specified command group.'''
    
    description = str(description or f'Have a conversation with {name}.')

    word_to_data: Dict[str, Tuple[Iterator[str], Iterator[int]]] = {}
    for word in TalkConfig.keys():
        data = cast(Dict[str, Dict[str, int]], TalkConfig[word])['next_words']         
        word_to_data[word] = tuple(zip(*data.items()))

    def choose_word(word: str):
        '''Chooses a random word to follow the provided word in the generated text.'''
        
        words, counts = word_to_data[word]
        return random.choices(words, weights=counts)[0]

    # attempt to add the command
    with catch((HTTPException, TypeError, CommandAlreadyRegistered), f'Talk :: Failed to load {name}\'s Markov chain!'):
        @group.command(name=name, description=description)
        async def _(interaction: Interaction) -> None:
            words: List[str] = []
            word: str = choose_word('')

            while word:
                words.append(word)
                word = choose_word(word)
                
            await interaction.response.send_message(' '.join(words))

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    talk = slash.Group(name='talk', description='Simulate conversations with people who don\'t want to talk to you.')

    add_talk_command(talk, 'kyoyo')
    
    tree.add_command(talk, guild=(DEBUG_GUILD if DEBUG else None))