from flask import Flask, render_template
from flask_socketio import SocketIO, disconnect, emit,send
import functools
from flask import request
from flask_cors import CORS, cross_origin
from fhe_client.FheClient import FheClient

app = Flask(__name__)
socketio = SocketIO(app,cors_allowed_origins="*")
CORS(app)

fhe_client = FheClient()
fhe_client.restful_predict("Fuck you")

@socketio.on('connect')
def test_connect():
    print(request.sid)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('send-message')
def handle_message(message):
    print('Client sent:',message)
    fhe_client.intecept(message)
    # emit('recieve-message', message,broadcast=True,include_self=False)

if __name__ == '__main__':
    socketio.run(app,debug=True,port=5001)
