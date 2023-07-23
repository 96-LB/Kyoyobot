import random
from discord import app_commands as slash, Client, Interaction, TextChannel
from typing import Any, Iterable
from uwuipy import uwuipy

UWU = uwuipy()

@slash.command()
async def ping(interaction: Interaction) -> None:
    '''Checks if Kyoyobot is running.'''
    
    await interaction.response.send_message('feet')

@slash.command()
async def ask(interaction: Interaction, question: str) -> None:
    '''Ask a question to the all-knowing Kyoyobot.'''
    
    # most responses from: https://en.wikipedia.org/wiki/Magic_8_Ball#Possible_answers
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
        'My toes point to yes.',
        'My toesies are tingling, yes!',
        # Neutral
        'Reply hazy, try again.',
        'Ask again later.',
        'Better not tell you now.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        'Offer more feet and try again.',
        # Negative
        'Don\'t count on it.',
        'My reply is no.',
        'My sources say no.',
        'Outlook not so good.',
        'Very doubtful.',
        'Kyoyo says no',
        'My toesies don\'t tingle :('
    ]
    
    response = random.choice(responses)
    if random.random() < 0.3:
        # 30% chance of uwuifying response
        response = UWU.uwuify(response) # type: ignore
    text = (
        f'Q: {question}\n'
        f'A: **{response}**'
    )
    
    await interaction.response.send_message(text)

@slash.command()
async def say(interaction: Interaction, channel: TextChannel, message: str) -> None:
    '''Instruct Kyoyobot to speak on your behalf.'''
    
    text = f'{interaction.user.mention} told me to say \"{message}\" in {channel.mention}\n'
    await channel.send(message)
    await interaction.response.send_message(text)

def setup(bot: Client) -> Iterable[slash.Command[Any, ..., Any] | slash.Group]:
    '''Sets up this bot module.'''
    
    return [ping, ask, say]
