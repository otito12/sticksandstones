import shutil
import requests
import os
from concrete.ml.deployment import FHEModelClient
import numpy as np
import pickle
from confluent_kafka import Consumer, Producer
import threading
import boto3
from botocore.client import Config
from io import BytesIO
import time
import sys

class FheClient():
    aws_config={
        "aws_key": 'AKIA5WXDWS4P7KLXQUUD',
        "aws_secret": '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',
        "aws_bucket": 'sticksnstones',
    }
    kafka_config={
        "bootstrap.servers": "pkc-lzvrd.us-west4.gcp.confluent.cloud:9092",
        "security.protocol": "sasl_ssl",
        "sasl.mechanism": "PLAIN",
        "group.id":"ss-chatroom-client",
        "message.max.bytes":"1000000000",
        "receive.message.max.bytes":"2147483647",
        "sasl.username": "7ELFNKFFNBRYAGCD",
        "sasl.password": "zXCGOM9BKXWeCQoioRDYzx6daKPo3vFh1PoK3ZHc0wYdBluUZEPnKMm/3bijwmP5",
    }
    bully_index = [
        "not_cyberbullying",
        "cyberbullying"
    ]
    path = os.getcwd()+'/fhe_client/client'

    def __init__(self,mediator_server_url="http://127.0.0.1:5050"):
        self.count_vector=None
        self.fhemodel_client=None
        self.mediator_server_url = mediator_server_url
        self._get_client_count()
        self._kafka_consumer = Consumer(self.kafka_config)
        temp = self.kafka_config.pop("group.id")
        self._kafka_poducer = Producer(self.kafka_config)
        self.kafka_config["group.id"]=temp
        self.active_messages={}
        self.aws_s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_config["aws_key"],
            aws_secret_access_key=self.aws_config["aws_secret"],
            config=Config(signature_version='s3v4')
        )
        kafka_consumer_thread = threading.Thread(target=self._listen_kafka_consumer)
        kafka_consumer_thread.daemon = True         # Daemonize thread
        kafka_consumer_thread.start()
        
    def _get_client_count(self):
        # get client.zip
        res = requests.get(self.mediator_server_url+"/initialize",stream=True)
        with open(self.path+ '/client.zip', 'wb') as out_file:
            shutil.copyfileobj(res.raw, out_file)
        self.fhemodel_client = FHEModelClient(self.path, os.getcwd())

        # get count_vector
        count_vector = requests.get(self.mediator_server_url+"/count_vector",stream=True)
        # with open(self.path+ '/count_vector.pkl', 'wb') as out_file:
        #     shutil.copyfileobj(, out_file)
        self.count_vector = pickle.loads(count_vector.raw.read())

        self._send_keys_to_server()
        
    def _send_keys_to_server(self): 
        self.fhemodel_client.generate_private_and_evaluation_keys()
        serialized_evaluation_keys = self.fhemodel_client.get_serialized_evaluation_keys()
        with open(self.path + "/serialized_keys.ekl", "wb") as f:
            f.write(serialized_evaluation_keys)
        files = {'file': open(self.path + '/serialized_keys.ekl', 'rb')}
        send_key_res = requests.post(self.mediator_server_url + '/keytoserver', files=files)
        if os.path.exists(self.path + "/serialized_keys.ekl"):
            os.remove(self.path + "/serialized_keys.ekl")
        else:
            print("The file does not exist")
    
    def _listen_kafka_consumer(self):
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
                    if self.active_messages.get(message_id,None):
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
                        # socket.send('recieve-message', message)

        except KeyboardInterrupt:
            pass
        finally:
            # Leave group and commit final offsets
            self._kafka_consumer.close()

    def intecept(self,message):
        
        for bucket in self.aws_s3.list_buckets()['Buckets']:
            print(bucket['Name'])
        print("intercepted: ",message)
        t0 = time.time()
        print("Let me think...")
        clear_input = np.array(self.count_vector.transform([message["message"]]).todense())
        encrypted_input = self.fhemodel_client.quantize_encrypt_serialize(clear_input)
        self.aws_s3.upload_fileobj(BytesIO(encrypted_input), self.aws_config["aws_bucket"], message['id'])
        url = "https://sticksnstones.s3.amazonaws.com/" + message['id']
        self._kafka_poducer.produce("encrypted-queue", value=message['id'])
        self.active_messages[message['id']+":pred"] = message
        t1 = time.time()
        print("...Done thinking")
        print("The currently Active Messages: ",self.active_messages)
        print(url)
        print("Encryption, AWS and Kafka Producton time:",t1-t0)
        print("Size of Encreypted text: ",sys.getsizeof(encrypted_input))
        
    def restful_predict(self,message):
        clear_input = np.array(self.count_vector.transform([message]).todense())
        encrypted_input = self.fhemodel_client.quantize_encrypt_serialize(clear_input)

        x = requests.post(self.mediator_server_url+'/predict', data=encrypted_input,
                        headers={'Content-Type': 'application/octet-stream'})
 
        decrypted_prediction = self.fhemodel_client.deserialize_decrypt_dequantize(
            x.content)[0]

        print(self.bully_index[np.argmax(decrypted_prediction)])

        


    