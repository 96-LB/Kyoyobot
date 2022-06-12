import json
from typing import Iterable

# This module is not for use with the bot, but rather as additional utility.

def dce_to_messages(filenames: Iterable[str], user_id: int):
    '''Extracts the specified user's messages from a set of DiscordChatExporter exports.'''

    output = []
    for filename in filenames:
        # attempt to load each file in JSON format
        try:
            with open(filename, encoding = 'cp850') as file:
                messages = json.loads(file.read()).get('messages', [])
        except:
            messages = []

        # check if the message is valid, and collect it if so
        for message in messages:
            if message.get('author', {}).get('id') == user_id:
                if message.get('type') == 'Default':
                    content = message.get('content')
                    if content is not None:
                        output.append(content)
    
    return output

def messages_to_markov(messages: Iterable[str]):
    '''Builds a Markov chain from the provided list of messages.''' 

    obj = {}

    def add_transition(current: str, next: str):
        '''Adds the specified transition to the Markov chain.'''
        
        if current not in obj:
            obj[current] = {}

        if next not in obj[current]:
            obj[current][next] = 0
            
        obj[current][next] += 1

    # processes each adjacent pair of words to build the transitions
    for message in messages:
        words = message.split()
        current = '' # represents the start and end of the message
        
        for next in words:
            add_transition(current, next)
            current = next
        add_transition(current, '')
    
    return obj

def export(markov: dict, name: str):
    '''Saves a Markov chain with the specified name.'''

    with open(f'data/markov/{name}.jason', 'w') as file:
        file.write(json.dumps(markov))
