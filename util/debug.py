import discord

def error(e: Exception, msg: str = None) -> None:
    '''Logs an error to the console.'''
    
    print('===ERROR!===')
    if msg is not None:
        print(f'ǁ {msg}')
    print(f'ǁ {repr(e)}')
    print('============')

# moved to prevent circular import
from util.settings import Env

DEBUG_GUILD: discord.Object = discord.Object(id=Env.get('DEBUG_GUILD', 0))