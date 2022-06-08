import discord

async def set_status(bot: discord.Client, message: str) -> None:
    '''Logs a message to the bot's status and the console.'''
    
    await bot.change_presence(activity=discord.Game(name=message))
    print(message)