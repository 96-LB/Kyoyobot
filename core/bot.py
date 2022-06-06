import os, discord
from utils.testing import TEST_GUILD

#set up the bot
intents = discord.Intents().default()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

@tree.command(guild=TEST_GUILD)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('feet')

@bot.event
async def on_ready():
    #starts up the bot
    await tree.sync(guild=TEST_GUILD)
    await bot.change_presence(activity=discord.Game(name='with feet'))
    print('kyoyobot is running!')


def run():
    bot.run(os.getenv('TOKEN'))