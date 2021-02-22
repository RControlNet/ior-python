from ior_research.mqtt import Communicator, createClient
import time

def on_message(payload):
    print(time.time() - float(payload['message']))

def run():
    token = "default"
    code = "5678"
    client = createClient(token, code)
    client.setOnReceive(lambda msg, payload: on_message(payload))

    while True:
        time.sleep(10)

if __name__ == "__main__":
    run()