import os, json
from discord import app_commands as slash, Interaction
from discord.app_commands import Group
from util.debug import DEBUG_GUILD
from util.config import CONFIG_PATH, load_sticker_config

DEBUG = True

class Stickers(Group):
    '''Command group used to hold all sticker commands. Commands are injected
    via generate_and_inject_sticker_command() inside setup().'''

def setup(tree):
    '''Sets up Stickers command group from config file.'''

    stickers = Stickers()

    def generate_and_inject_sticker_command(name: str, image_url: str):
        '''Generates a generic sticker commmand and injects it into the specified
        command group.'''

        async def base_command(interaction: Interaction):
            await interaction.response.send_message(image_url)

        command = slash.command()(base_command)
        setattr(command, 'name', name)
        stickers._children[name] = command
        setattr(stickers, name, command) 

    sticker_configs = load_sticker_config()
    for sticker_config in sticker_configs:
        generate_and_inject_sticker_command(sticker_config['name'], sticker_config['image_url'])

    tree.add_command(stickers, guild=(DEBUG_GUILD if DEBUG else None))