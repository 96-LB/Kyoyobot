import random
from discord import app_commands as slash, Client, Interaction, TextChannel
from util.debug import DEBUG_GUILD

DEBUG = False

# This command will have the bot send a message to a specified text channel 
# bot will announce the user who initiated the command in the current channel
@slash.command()
async def say(interaction: Interaction, channel: TextChannel, message: str) -> None:
    '''Have Kyoyobot say something in a channel.'''
    
    text = f'{interaction.user.mention} told me to say \"{message}\" in {channel.mention}\n'
    await channel.send(message)
    await interaction.response.send_message(text) 
    

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    tree.add_command(say, guild=(DEBUG_GUILD if DEBUG else None))

