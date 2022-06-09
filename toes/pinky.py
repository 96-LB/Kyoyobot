from discord import app_commands as slash, Client, Interaction
from util.debug import DEBUG_GUILD

DEBUG = False

@slash.command()
async def ping(interaction: Interaction) -> None:
    '''Checks if the bot is running.'''
    
    await interaction.response.send_message('feet')

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    tree.add_command(ping, guild=(DEBUG_GUILD if DEBUG else None))