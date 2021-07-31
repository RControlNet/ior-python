import time, sys

from pygments.lexer import default


def on_receive(x):
    """Create a Receive message function, that takes a dict object"""
    print("Received",time.time() - float(x['message']))

if __name__ == "__main__":
    sys.path.append("../") # Append Parent folder path to System Environment Path
    from ior_research.IOTClient import IOTClientWrapper # Import IOTClientWrapper
    import argparse
    # Build Config Object, you can supply various keyword argument to below dict object
    config = {
        "server": "localhost",
        "httpPort": 5001,
        "tcpPort": 8000,
        "useSSL": False
    }
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('from', default="../config/from.jsom")
    parser.add_argument('to', default="../config/to.jsom")

    args = parser.parse_args().__dict__

    # Create a Client #1 Configuration
    configFrom = config.copy()
    configFrom['file'] = args['from']

    # Create Client #2 Configuration
    configTo = config.copy()
    configTo['file'] = args['to']

    token = "default" # Define and Assign Token, "default" is the default token value

    # Instanciate IOTClientWrapper Object,
    client1 = IOTClientWrapper(token,config=configFrom)
    client2 = IOTClientWrapper(token,config=configTo)

    # Set on receive function, so that if a message is received this function should be called to execute some task
    client2.set_on_receive(on_receive)


    client1.start()     # Start first client
    client2.start()     # Start second client

    try:
        while True:
            # Send a message at a frequency of 1 Hz
            print("Sending Message")
            client1.sendMessage(message = str(time.time()))
            time.sleep(1)
    finally:
        exit()

