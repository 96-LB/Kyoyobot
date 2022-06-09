from discord import app_commands as slash, Interaction, Client
from discord.errors import HTTPException
from discord.app_commands.errors import CommandAlreadyRegistered
from util.debug import DEBUG_GUILD, error
from util.settings import Config

DEBUG = False

def add_sticker_command(group: slash.Group, name: str, url: str, description: str = ''):
    '''Generates a sticker commmand and adds it to the specified command group.'''

    description = str(description or f'Posts the {name} sticker.')

    #attempt to add the command and return whether it succeeded
    try:
        @group.command(name=name, description=description)
        async def _(interaction: Interaction) -> None:
            await interaction.response.send_message(str(url))
            
        return True
        
    except (HTTPException, TypeError, CommandAlreadyRegistered) as e:
        error(e, f'Failed to add {name} sticker!')
        
        return False
    
def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    stickers = slash.Group(name='stickers', description='Posts stickers from a preset collection.')

    #load each sticker command from the configuration file
    sticker_configs = Config.get('stickers', [])
    for sticker_config in sticker_configs:
        name = sticker_config.get('name')
        url = sticker_config.get('url')
        description = sticker_config.get('description')
        
        add_sticker_command(stickers, name, url, description)

    tree.add_command(stickers, guild=(DEBUG_GUILD if DEBUG else None))