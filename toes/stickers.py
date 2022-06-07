from discord import app_commands as slash, Interaction
from util.debug import DEBUG_GUILD
from util.config import load_sticker_config

DEBUG = False

def add_sticker_command(group: slash.Group, name: str, url: str, description: str=None):
    '''Generates a sticker commmand and adds it to the specified command group.'''

    description = description if description is not None else f'Posts the {name} sticker.'

    @group.command(name=name, description=description)
    async def _(interaction: Interaction):
        await interaction.response.send_message(url)

def setup(tree):
    '''Sets up this command group.'''

    stickers = slash.Group(name='stickers', description='Posts stickers from a preset collection.')

    #load each sticker command from the configuration file
    sticker_configs = load_sticker_config()
    for sticker_config in sticker_configs:
        add_sticker_command(stickers, sticker_config['name'], sticker_config['url'])

    tree.add_command(stickers, guild=(DEBUG_GUILD if DEBUG else None))