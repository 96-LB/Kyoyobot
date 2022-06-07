import os, json

CONFIG_PATH = os.path.join(os.getcwd(), 'config.json') 

def load_sticker_config():
    '''Loads and returns list of sticker configs from config.json.'''

    with open(CONFIG_PATH, 'r') as file:
        config = json.loads(file.read())
        return config['stickers']