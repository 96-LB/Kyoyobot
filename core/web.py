from flask import Flask
from threading import Thread

app = Flask('Kyoyobot')

@app.route('/')
def route_index():
    '''Receives pings to keep the server running.'''
    
    return '🐛'

def launch_server():
    '''Starts a server to receive pings that keep the application awake.'''
    
    app.run(host='0.0.0.0', port=8080)

def run():
    '''Runs this module.'''

    #imagine paying for server hosting 🐛
    server = Thread(target=launch_server)
    server.start()