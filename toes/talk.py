import os, random
from discord import app_commands as slash, Client, Interaction, Message
from discord.errors import HTTPException
from discord.app_commands.errors import CommandAlreadyRegistered
from typing import Any, Callable, Iterable, Sequence, Tuple

from util.debug import DEBUG, DEBUG_GUILD, catch
from util.settings import json_settings

PATH = 'data/markov/'

def get_markov(name: str) -> Callable[[], str]:
    '''Builds a Markov chain using the specified user's messages.'''
    
    config = json_settings(f'data/markov/{name}.jason')
    
    # load the data from the markov chain data file
    word_data: dict[str, Tuple[Sequence[str], Sequence[int]]] = {}
    for word in config.keys():
        data: dict[str, int] = config[word]
        word_data[word] = (tuple(data.keys()), tuple(data.values()))
    
    def choose_word(word: str):
        '''Chooses a random word to follow the provided word in the generated text.'''
        
        words, counts = word_data[word]
        return random.choices(words, weights=counts)[0]
    
    def markov() -> str:
        '''Generates a message using the Markov chain.'''
        
        words: list[str] = []
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

def setup(bot: Client) -> Iterable[slash.Command[Any, ..., Any] | slash.Group]:
    '''Sets up this bot module.'''
    
    # respond to mentions with kyoyo's markov chain
    markov = get_markov('kyoyo')
    
    async def on_message(message: Message) -> None:
        # ignore messages sent by the bot to prevent infinite loops
        if message.author == bot.user:
            return
        
        # if in debug mode, only respond in direct messages or the debug server
        if DEBUG and not (message.guild is None or message.guild.id == DEBUG_GUILD.id):
            return
        
        # respond to mentions with the markov chain
        if bot.user is not None and bot.user.mentioned_in(message):
            await message.channel.send(markov())
    bot.event(on_message)
    
    # also add each available markov chain as a slash command
    talk = slash.Group(name='talk', description='Simulate conversations with people who don\'t want to talk to you.')
    
    # load each markov chain from the data folder
    for name in os.listdir(PATH):
        if name.endswith('.jason'):
            add_talk_command(talk, name[:-6])
    
    return [talk]
