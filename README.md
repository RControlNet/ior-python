## IOT Client - Python

IOT is taking over world, many electronics device connect together on a network and communicate to each other.
I have build app that helps you to connect those microcontroller together. Below are the client details.

Before going further this project is strongly meant for controlling robots over internet, you can check out more on <a href="https://iorresearch.ml">Project Website</a>

Currently it has been tested on:
    Arduino, Lego Mindstroms EV3 Brick and on a Raspberry PI 3
    other tests are being done.

This is git repository for  the python client:

## Server Setup (Quick Start)

    cd ~
    mkdir controlnet-docker
    cd controlnet-docker
    wget https://mayank31313.github.io/docker/socket_server/docker-compose.yml
    
    docker-compose up

## Client Start (Quick Start)

    cd /to/project/
    cd examples
    python3 LatencyCheck.py
    
## Installation
Run the following command

    python3 setup.py install
 
## Usage

    config = {
        "server": "localhost",
        "httpPort": 5001,
        "socketServer": "localhost",
        "tcpPort": 8000,
        #"useSSL": True    # Optional
    }
    
## Create Instance of IOT Client

    from ior_research.IOTClient import IOTClientWrapper
    iot = IOTClientWrpper(token=token, config = config) #Creating object for IOT Client

### Setting up Receive Function to do some Operation when a response is received.

    iot.set_on_receive(lambda x: print(x))

### Last but not the least start the IOTClient

    iot.start()
    iot.join() #Since IOTClient inherites Thread Class you can also use .join() function depending on your use case


    


