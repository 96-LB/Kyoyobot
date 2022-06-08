from discord import app_commands as slash, Interaction
from util.debug import DEBUG_GUILD
from util.settings import Config

DEBUG = False

def add_sticker_command(group: slash.Group, name: str, url: str, description: str=None):
    '''Generates a sticker commmand and adds it to the specified command group.'''

    if name is None or url is None:
        return

    description = description if description is not None else f'Posts the {name} sticker.'

    @group.command(name=name, description=description)
    async def _(interaction: Interaction):
        await interaction.response.send_message(url)

def setup(tree):
    '''Sets up this command group.'''

    stickers = slash.Group(name='stickers', description='Posts stickers from a preset collection.')

    #load each sticker command from the configuration file
    sticker_configs = Config.get('stickers', {})
    for sticker_config in sticker_configs:
        add_sticker_command(stickers, **sticker_config)

    tree.add_command(stickers, guild=(DEBUG_GUILD if DEBUG else None))