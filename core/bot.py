import os, discord
from importlib import import_module
from util.bot import set_status
from util.debug import DEBUG_GUILD
from util.settings import Env

#set up the discord client
intents = discord.Intents().default()
intents.messages = True
intents.message_content = True
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    '''Initializes the bot.'''

    await set_status(bot, 'loading toes...')

    #iterates over and loads every command group in the toes folder
    toes = [toe.replace('.py', '') for toe in os.listdir('toes') if '.py' in toe]
    for toe in toes:
        await set_status(bot, f'loading {toe} toe...')
        try:
            module = import_module(f'toes.{toe}')
            module.setup(bot, tree)
        except Exception as e:
            await set_status(bot, f'failed to load {toe} toe!')
            raise e

    #loads the global commands and the debug commands
    await tree.sync()
    await tree.sync(guild=DEBUG_GUILD)

    #notifies that the bot is ready
    await set_status(bot, 'with feet')

def run():
    '''Runs this module.'''
    
    bot.run(Env.get('TOKEN'))