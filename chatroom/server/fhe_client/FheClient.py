import shutil
import requests
import os
from concrete.ml.deployment import FHEModelClient
import numpy as np
import pickle

class FheClient():
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

    def predict(self,text):
        clear_input = np.array(self.count_vector.transform([text]).todense())
        encrypted_input = self.fhemodel_client.quantize_encrypt_serialize(clear_input)

        x = requests.post(self.mediator_server_url+'/predict', data=encrypted_input,
                        headers={'Content-Type': 'application/octet-stream'})
 
        decrypted_prediction = self.fhemodel_client.deserialize_decrypt_dequantize(
            x.content)[0]

        print(self.bully_index[np.argmax(decrypted_prediction)])

    