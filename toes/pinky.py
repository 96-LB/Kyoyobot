import random
from discord import app_commands as slash, Client, Interaction
from util.debug import DEBUG_GUILD
from util.talk import TalkGenerator

DEBUG = False

@slash.command()
async def ping(interaction: Interaction) -> None:
    '''Checks if the bot is running.'''
    
    await interaction.response.send_message('feet')

@slash.command()
async def ask(interaction: Interaction, question: str) -> None:
    '''Ask a question to the all-knowing Kyoyobot.'''

    # responses from: https://en.wikipedia.org/wiki/Magic_8_Ball#Possible_answers
    responses = [
        # Positive 
        'It is certain.',
        'It is decidedly so.',
        'Without a doubt.',
        'Yes definitely.',
        'You may rely on it.',
        'As I see it, yes.',
        'Most likely.',
        'Outlook good.',
        'Yes.',
        'Signs point to yes.',
        # Neutral
        'Reply hazy, try again.',
        'Ask again later.',
        'Better not tell you now.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        # Negative
        'Don\'t count on it.',
        'My reply is no.',
        'My sources say no.',
        'Outlook not so good.',
        'Very doubtful.',
	'Kyoyo says no'

    ]

    text = (
        f'Q: {question}\n'
        f'A: **{random.choice(responses)}**'
    )

    await interaction.response.send_message(text)

@slash.command()
async def talk(interaction: Interaction) -> None:
    '''Talk to your one true friend, Kyoyobot.'''

    await interaction.response.send_message(TalkGenerator.generate())

def setup(bot: Client, tree: slash.CommandTree) -> None:
    '''Sets up this bot module.'''

    TalkGenerator.setup()

    tree.add_command(ping, guild=(DEBUG_GUILD if DEBUG else None))
    tree.add_command(ask, guild=(DEBUG_GUILD if DEBUG else None))
    tree.add_command(talk, guild=(DEBUG_GUILD if DEBUG else None))
