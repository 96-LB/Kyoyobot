import random
from discord import app_commands as slash, Client, Interaction, TextChannel
from util.debug import DEBUG_GUILD

DEBUG = False

@slash.command()
async def say(interaction: Interaction, channel: TextChannel, message:str,) -> None:
    '''Have Kyoyobot say something in a channel.'''
    
    text = f'You told me to say \"{message}\" in #{channel.name}\n'
    await channel.send(message)
    await interaction.response.send_message(text)
    

#@say.autocomplete('channel')
#async def channels_autocomplete(interaction: Interaction, current: str) -> list[slash.Choice[str]]:
#    channels = []
#    for item in Client.get_all_channels():
#        channels.append(item)
#    return [slash.Choice(name=channel, value=channel) for channel in channels if current.lower() in channel.name]




def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    tree.add_command(say, guild=(DEBUG_GUILD if DEBUG else None))

