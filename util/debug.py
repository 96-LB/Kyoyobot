import discord
from util.settings import Env

DEBUG_GUILD = discord.Object(id=Env.get('DEBUG_GUILD', 0))