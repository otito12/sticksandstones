from confluent_kafka import Consumer, Producer
import json
import numpy as np

kafka_config={
    "bootstrap.servers": "pkc-lzvrd.us-west4.gcp.confluent.cloud:9092",
    "security.protocol": "sasl_ssl",
    "sasl.mechanism": "PLAIN",
    "group.id":"python_example_group_1",
    "sasl.username": "4UWMU4B6UGYYOIRH",
    "sasl.password": "r9tsYZipOZ6r8GFM78GtrW2cg4ybXTsGeeD0auDbh6Dp3YZxGY2CvlMZMIkiWar+",
}
# Parse the command line.
c = Consumer(kafka_config)
kafka_config.pop("group.id")
p = Producer(kafka_config)

c.subscribe(['mediate-queue'])

if __name__ == '__main__':
    try:
        while True:
            msg = c.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                # print("waiting..")
                continue
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                # Extract the (optional) key and value, and print.
                print("EVENT ARRIVED")
                print("Consumed event from topic {}: value = {}".format(
                    msg.topic(), msg.value()))
                message_obj = json.loads(msg.value())
                if (np.random.randint(0,2)):
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
    
    
