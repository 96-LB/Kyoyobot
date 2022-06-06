from flask import Flask
from threading import Thread

app = Flask('Kyoyobot')

@app.route('/')
def route_index():
    #sets up a throwaway route for the flask app
    return '🐛'

def launch_server():
    #runs the flask app
    app.run(host='0.0.0.0', port=8080)

def run():
    #runs a server that gets pinged periodically so that the bot doesn't shut off
    #imagine paying for server hosting 🐛
    server = Thread(target=launch_server)
    server.start()