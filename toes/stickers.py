from discord import app_commands as slash, Client, Interaction
from discord.errors import HTTPException
from discord.app_commands.errors import CommandAlreadyRegistered
from typing import Iterable, Union

from util.debug import catch
from util.settings import Config

def add_sticker_command(group: slash.Group, name: str, url: str, description: str = '') -> None:
    '''Generates a sticker commmand and adds it to the specified command group.'''
    
    description = str(description or f'Posts the {name} sticker.')
    
    # attempt to add the command and return whether it succeeded
    with catch((HTTPException, TypeError, CommandAlreadyRegistered), f'Stickers :: Failed to add {name} sticker!'):
        @group.command(name=name, description=description)
        async def _(interaction: Interaction) -> None:
            await interaction.response.send_message(str(url))
    
def setup(bot: Client) -> Iterable[Union[slash.Command, slash.Group]]:
    '''Sets up this bot module.'''
    
    stickers = slash.Group(name='stickers', description='Posts stickers from a preset collection.')
    
    # load each sticker command from the configuration file
    sticker_configs = []
    with catch(TypeError, 'Stickers :: Failed to load sticker configuration!'):
        sticker_configs = list(Config.get('stickers')) # type: ignore
    
    for sticker_config in sticker_configs:
        name = sticker_config.get('name')
        url = sticker_config.get('url')
        description = sticker_config.get('description')
        
        add_sticker_command(stickers, name, url, description)
    
    return [stickers]
