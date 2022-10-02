import os, random
from discord import app_commands as slash, Client, Interaction, Message
from discord.errors import HTTPException
from discord.app_commands.errors import CommandAlreadyRegistered
from typing import Callable, Dict, List, Sequence, Tuple
from util.debug import DEBUG_GUILD, catch
from util.settings import json_settings

DEBUG = False
PATH = 'data/markov/'

def get_markov(name: str) -> Callable[[], str]:
    '''Builds a Markov chain using the specified user's messages.'''
    
    config = json_settings(f'data/markov/{name}.jason')

    # load the data from the markov chain data file
    word_data: Dict[str, Tuple[Sequence[str], Sequence[int]]] = {}
    for word in config.keys():
        # these types can't be inferred so we can just ignore for now
        # we should do some error checking later though
        data = config[word] # type: ignore
        word_data[word] = tuple(zip(*data.items())) # type: ignore

    def choose_word(word: str):
        '''Chooses a random word to follow the provided word in the generated text.'''
        
        words, counts = word_data[word]
        return random.choices(words, weights=counts)[0]

    def markov() -> str:
        '''Generates a message using the Markov chain.'''
        
        words: List[str] = []
        word: str = choose_word('')

        # the empty string represents the start and end of the message
        while word:
            words.append(word)
            word = choose_word(word)
               
        return ' '.join(words)

    return markov

def add_talk_command(group: slash.Group, name: str, description: str = '') -> None:
    '''Generates a talk commmand and adds it to the specified command group.'''
    
    description = str(description or f'Have a conversation with {name.capitalize()}.')
    markov = get_markov(name)

    # attempt to add the command
    with catch((HTTPException, TypeError, CommandAlreadyRegistered), f'Talk :: Failed to load {name}\'s Markov chain!'):
        @group.command(name=name, description=description)
        async def _(interaction: Interaction) -> None:
            await interaction.response.send_message(f'{name.capitalize()}: {markov()}')

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    talk = slash.Group(name='talk', description='Simulate conversations with people who don\'t want to talk to you.')

    # load each markov chain from the data folder
    for name in os.listdir(PATH):
        if name.endswith('.jason'):
            add_talk_command(talk, name[:-6])
    
    tree.add_command(talk, guild=(DEBUG_GUILD if DEBUG else None))

    # also respond to mentions with kyoyo's markov chain
    markov = get_markov('kyoyo')
    
    @bot.event
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot to prevent infinite loops
        if message.author == bot.user:
            return
        
        # execute the master trigger if not in debug mode
        if not DEBUG or (message.guild is not None and message.guild.id == DEBUG_GUILD.id):
            if bot.user is not None and bot.user.mentioned_in(message):
                await message.channel.send(markov())
