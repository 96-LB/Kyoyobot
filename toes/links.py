from discord import app_commands as slash, Client, Interaction
from discord.errors import HTTPException
from discord.app_commands.errors import CommandAlreadyRegistered
from typing import Any, Iterable, cast

from util.debug import catch
from util.settings import Config

def add_link_command(group: slash.Group, name: str, url: str, description: str = '') -> None:
    '''Generates a link commmand and adds it to the specified command group.'''
    
    description = str(description or f'Posts a link to {name}.')
    
    # attempt to add the command and return whether it succeeded
    with catch((HTTPException, TypeError, CommandAlreadyRegistered), f'Links :: Failed to add {name} link!'):
        @group.command(name=name, description=description)
        async def _(interaction: Interaction) -> None:
            await interaction.response.send_message(str(url), ephemeral=True)

def setup(bot: Client) -> Iterable[slash.Command[Any, ..., Any] | slash.Group]:
    '''Sets up this bot module.'''
    
    links = slash.Group(name='links', description='A quick reference of useful links.')
    
    # load each link command from the configuration file
    link_configs: list[dict[str, Any]] = []
    with catch(TypeError, 'Links :: Failed to load link configuration!'):
        link_configs = cast(list[dict[str, Any]], Config.get('links'))
    
    for link_config in link_configs:
        name = link_config.get('name', '')
        url = link_config.get('url', '')
        description = link_config.get('description', '')
        
        add_link_command(links, name, url, description)
    
    return [links]
