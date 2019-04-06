## IOT Client - Python

IOT is taking over world, many electronics device connect together on a network and communicate to each other.
I have build app that helps you to connect those microcontroller together. Below are the client details.

Currently it has been tested on:
    Arduino, Lego Mindstroms EV3 Brick and on a Raspberry PI 3
    other tests are being done.


This is git repository for  the python client:

    token = "paste your subscription key here"
    code = int("current device code here")
    to = int("Destiation device code here")

    time_delay = 90 # Time delay for the heart beat (in seconds) default is 90 seconds

## Create Instance of IOT Client

    iot = IOTClient(from = code,to=to,token=token) #Creating object for IOT Client

### Setting up Receive Function to do some Operation when a response is Received.

    iot.set_on_receive(lambda x: print(x))

### Last but not the least start the IOTClient

    iot.start()
    
Since IOTClient inherites Thread Class you can also use .join() function depending on your use
    
    iot.join()


