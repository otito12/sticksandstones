from confluent_kafka import Consumer, Producer
import json
import numpy as np
import pickle
import shutil
from flask import Flask, jsonify, request, flash, request, send_file
from flask_cors import CORS
import requests
from concrete.ml.deployment import FHEModelClient, FHEModelDev, FHEModelServer
from werkzeug.utils import secure_filename
import os
import platform
import time
import threading
import boto3
from botocore.client import Config
from io import BytesIO

aws_config={
    "aws_key": 'USERNAME',
    "aws_secret": 'PASSWORD',
    "aws_bucket": 'sticksnstones',
}

kafka_config={
    "bootstrap.servers": "pkc-lzvrd.us-west4.gcp.confluent.cloud:9092",
    "security.protocol": "sasl_ssl",
    "sasl.mechanism": "PLAIN",
    "group.id":"python_example_group_1",
    "message.max.bytes":"1000000000",
    "receive.message.max.bytes":"2147483647",
    "sasl.username": "USERNAME",
    "sasl.password": "PASSWORD",
}

# AWS client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_config["aws_key"],
    aws_secret_access_key=aws_config["aws_secret"],
    config=Config(signature_version='s3v4')
)

# Parse the command line.
c = Consumer(kafka_config)
kafka_config.pop("group.id")
p = Producer(kafka_config)

c.subscribe(['mediate-queue','encrypted-queue'])
clf = pickle.load(open('model.pkl','rb'))
count_vect = pickle.load(open('count_vect.pkl','rb'))

def model_pedict(text):
  return clf.predict(count_vect.transform([text]))[0]

server_dir = os.getcwd()

ALLOWED_EXTENSIONS = {'ekl', 'zip', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd()
CORS(app)


@app.route("/")
def hello_world():
    return jsonify("Hello world form server")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/initialize", methods=["GET"])
def initalize():
    return send_file("client.zip")

@app.route("/count_vector", methods=["GET"])
def count_vector():
    return send_file("cml_cv.pkl")

@app.route("/keytoserver", methods=["POST"])
def key_to_server():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return jsonify("You fucking nob"), 400
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return jsonify("You fucking nob"), 400
        if file and allowed_file(file.filename):
            # use client id as filename when multi
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            return jsonify("You fucking nob, you did it!")
        
@app.route("/predict", methods=["POST"])
def predict():
    if request.method == 'POST':
        file = request.data
        # use client id as filename when multi
        with open(server_dir + "/serialized_keys.ekl", "rb") as f:
            serialized_evaluation_keys = f.read()
        encrypted_prediction = FHEModelServer(os.getcwd()).run(
            file, serialized_evaluation_keys
        )
        return encrypted_prediction
    
def _listen():
    print("Encrypted Listening")
    # expecting byte string
    try:
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                # Extract the (optional) key and value, and print.
                print("EVENT ARRIVED")
                if(msg.topic() == "encrypted-queue"):
                    print("Consumed encrypted event from topic {}: value = {}".format(
                    msg.topic(), msg.value()))
                    
                    message_id = msg.value().decode("utf-8")
                    aws_file_key = message_id + ":pred"
                    print("I AM THE MESSAGE ID FROM KAFKA:", message_id)

                    t0 = time.time()
                    print("Let me think...")
                    # download file from aws link
                    encrypted_input = s3.get_object(Bucket=aws_config['aws_bucket'],Key=message_id)['Body'].read()

                    # peform prediction
                    with open(server_dir + "/serialized_keys.ekl", "rb") as f:
                        serialized_evaluation_keys = f.read()
                    encrypted_prediction = FHEModelServer(os.getcwd()).run(
                        encrypted_input, serialized_evaluation_keys
                    )
                    
                    # upload prediction result to aws
                    s3.upload_fileobj(BytesIO(encrypted_prediction), aws_config["aws_bucket"], aws_file_key)
                    
                    # publish link to encypted stream 
                    p.produce("encrypted-pred-queue", value=aws_file_key)

                    # delete 240MB!!!! encrypted message
                    s3.delete_object(Bucket=aws_config["aws_bucket"], Key=message_id)
                    t1 = time.time()
                    print("...Done thinking")
                    print(aws_file_key)
                    print("Prediction, AWS and Kafka Producton time:",t1-t0)
                    
                else:
                    print("Consumed event from topic {}: value = {}".format(
                    msg.topic(), msg.value()))
                    message_obj = json.loads(msg.value())
                    if (model_pedict(message_obj["message"])):
                        message_obj.update({"flagged":True})
                        p.produce("flagged-queue", value=json.dumps(message_obj))
                        print("Message Flagged")
                        print("NEW_OBJ\n",message_obj)
                    else:
                        p.produce("clean-queue", value=json.dumps(message_obj))
                        print("Message Clean")
                        print("NEW_OBJ\n",message_obj)
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        c.close()
        
def _start_app():
    app.run(port=5050)

if __name__ == '__main__':
    _app_thread = threading.Thread(target=_start_app)
    _kafka_thread = threading.Thread(target=_listen)
 
    # starting threads
    _app_thread.start()
    _kafka_thread.start()
 
    _app_thread.join()
    _kafka_thread.join()
   
    
    
