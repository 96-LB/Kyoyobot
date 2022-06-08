from discord import app_commands as slash, Interaction
from util.debug import DEBUG_GUILD

DEBUG = False

@slash.command()
async def ping(interaction: Interaction) -> None:
    '''Checks if the bot is running.'''
    
    await interaction.response.send_message('feet')

def setup(tree: slash.CommandTree) -> None:
    '''Sets up this command group.'''

    tree.add_command(ping, guild=(DEBUG_GUILD if DEBUG else None))