import discord
from contextlib import contextmanager
from typing import Generator, Tuple, Type, Union

async def set_status(bot: discord.Client, message: str) -> None:
    '''Logs a message to the bot's status and the console.'''
    
    await bot.change_presence(activity=discord.Game(name=message))
    print(message)

def error(e: Exception, msg: str = None) -> None:
    '''Logs an error to the console.'''
    
    print('===ERROR!===')
    if msg is not None:
        print(f'ǁ {msg}')
    print(f'ǁ {repr(e)}')
    print('============')

@contextmanager
def catch(types : Union[Type, Tuple[Type, ...]], msg : str = None) -> Generator[None, None, None]:
    '''Catches and handles the specified exception and logs it to the console.'''
    
    try:
        yield
    except Exception as e:
        # handle it only if the type matches
        if isinstance(e, types):
            error(e, msg)
        else:
            raise
    

# moved to prevent circular import
from util.settings import Env

DEBUG_GUILD: discord.Object = discord.Object(id=Env.get('DEBUG_GUILD', '0'))
