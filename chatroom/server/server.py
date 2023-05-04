from flask import Flask, render_template
from flask_socketio import SocketIO, disconnect, emit,send
import functools
from flask import request
from flask_cors import CORS, cross_origin
from fhe_client.FheClient import FheClient
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app,cors_allowed_origins="*")
CORS(app)

fhe_client = FheClient(app,socketio)
fhe_client.restful_predict("Fuck you")

def _listen_kafka_consumer(self):
        with self.app.test_request_context('/'):
            self._kafka_consumer.subscribe(['encrypted-pred-queue'])
            print("Listening")
            try:
                while True:
                    msg = self._kafka_consumer.poll(1.0)
                    if msg is None:
                        continue
                    elif msg.error():
                        print("ERROR: %s".format(msg.error()))
                    else:
                        # Extract the (optional) key and value, and print.
                        print("EVENT ARRIVED From Kafka Consumer")
                        print("Consumed event from topic {}: value = {}".format(
                            msg.topic(), msg.value()))
                        
                        message_id = msg.value().decode("utf-8")
                        # when message arrives go to AWS to get pred file
                        encrypted_prediciton = self.aws_s3.get_object(Bucket=self.aws_config['aws_bucket'],
                                                                    Key=message_id)['Body'].read()

                        # decyrpt
                        decrypted_prediction = self.fhemodel_client.deserialize_decrypt_dequantize(encrypted_prediciton)[0]
                        message = self.active_messages.pop(message_id)
                        if (np.argmax(decrypted_prediction)):
                            message["flagged"]=True
                        print(message)

                        # the final fucking mini boss
                        self.socket.emit('recieve-message', message,include_self=False)

            except KeyboardInterrupt:
                pass
            finally:
                # Leave group and commit final offsets
                self._kafka_consumer.close()

@socketio.on('connect')
def test_connect():
    print(request.sid)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('send-message')
def handle_message(message):
    fhe_client.intecept(message)
    # emit('recieve-message', message,broadcast=True,include_self=False)

if __name__ == '__main__':
    socketio.run(app,debug=True,port=5001)
