from flask import Flask
from flask.typing import ResponseReturnValue
from threading import Thread
from util.settings import Env

app: Flask = Flask('Kyoyobot')

@app.route('/')
def route_index() -> ResponseReturnValue:
    '''Receives pings to keep the server running.'''
    
    return '🐛'

def launch_server() -> None:
    '''Starts a server to receive pings that keep the application awake.'''
    
    app.run(host='0.0.0.0', port=8080)

def run() -> None:
    '''Runs this module.'''
 
    # imagine paying for server hosting 🐛
    if Env.get('HOST') == 'R':
        server = Thread(target=launch_server)
        server.start()
