import discord
from contextlib import contextmanager
from typing import Any, Generator, Optional, Tuple, Type

async def set_status(bot: discord.Client, message: str) -> None:
    '''Logs a message to the bot's status and the console.'''
    
    await bot.change_presence(activity=discord.Game(name=message))
    print(message)

def error(e: Exception, msg: Optional[str] = None) -> None:
    '''Logs an error to the console.'''
    
    print('===ERROR!===')
    if msg is not None:
        print(f'ǁ {msg}')
    print(f'ǁ {repr(e)}')
    print('============')

@contextmanager
def catch(types: Type[Any] | Tuple[Type[Any], ...], msg: Optional[str] = None) -> Generator[None, None, None]:
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

DEBUG: bool = bool(Env.get('DEBUG', False))
DEBUG_GUILD: discord.Object = discord.Object(id=str(Env.get('DEBUG_GUILD', 1059681961515425793)))
