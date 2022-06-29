import discord, os, subprocess
from discord.errors import HTTPException
from functools import wraps
from importlib import import_module
from typing import Any, Callable, Coroutine, TypeVar, cast
from util.debug import DEBUG_GUILD, error, set_status
from util.settings import Env

Coro = TypeVar('Coro', bound=Callable[..., Coroutine[Any, Any, Any]])
class Bot(discord.Client):
    '''Extends a client to provide support for multiple event handlers.'''

    def event(self, new: Coro, /) -> Coro:
        '''Registers a new event without obliterating the old one.'''
        
        old: Coro = getattr(self, new.__name__, None) # type: ignore

        function: Coro = new
        if old is not None:
            # run both the old function and the new one
            @wraps(new)
            async def wrapper(*args, **kwargs) -> None:
                await old(*args, **kwargs)
                await new(*args, **kwargs)
            function = cast(Coro, wrapper) # why do we have to cast?
        
        return super().event(function)

# set up the discord client
intents = discord.Intents().default()
intents.messages = True
intents.message_content = True
bot = Bot(intents=intents)
tree = discord.app_commands.CommandTree(bot)

@bot.event
async def on_ready() -> None:
    '''Initializes the bot.'''

    await set_status(bot, 'loading toes...')

    # iterates over and loads every command group in the toes folder
    toes = [toe.replace('.py', '') for toe in os.listdir('toes') if '.py' in toe]
    for toe in toes:
        print(f'loading {toe} toe...')
        try:
            module = import_module(f'toes.{toe}')
            module.setup(bot, tree) # type: ignore
        except Exception as e:
            await set_status(bot, f'failed to load {toe} toe!')
            raise e

    # loads the global commands and the debug commands
    await tree.sync()
    await tree.sync(guild=DEBUG_GUILD)

    # notifies that the bot is ready
    await set_status(bot, 'with feet')

def run() -> None:
    '''Runs this module.'''

    try:
        bot.run(Env.get('TOKEN'))
    except HTTPException as e:
        if Env.get('HOST') == 'R':
            error(e, 'Failed to start bot! Restarting...')
            subprocess.run(['kill', '1'])
        else:
            raise
