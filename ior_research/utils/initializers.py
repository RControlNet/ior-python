from yaml import load, Loader
import os, time, sys
try:
    import ior_research
except ModuleNotFoundError:
    sys.path.append("../../")
from ior_research.utils.filterchains import MessageFilterChain, RControlNetMessageFilter
from ior_research.IOTClient import IOTClientWrapper
from ior_research.utils.video import VideoTransmitter, createVideoTransmitter

class Credentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class ProjectConfig:
    def __init__(self, **kwargs):
        self.clientCredentialsPath = kwargs['clientJson']
        self.clientCredentialsPath = tuple(map(lambda x:
                                            os.path.join(os.path.dirname(kwargs['controlnetConfig']),
                                                x) if not os.path.isabs(x) else x,
                                         self.clientCredentialsPath
                                         ))
        self.token = kwargs['token']
        self.videoConfigs = kwargs['streamer'] if 'streamer' in kwargs else None
        self.credentials =kwargs['credentials']
        self.credentials = Credentials(**self.credentials)

class Initializer:
    def __init__(self, configPath):
        self.projectConfig = loadConfig(configPath)
        self.filterChains = []
        self.transmitter = None
        self.clients = []

        firstFilter = RControlNetMessageFilter(self)
        self.filterChains.append(firstFilter)

    def addFilter(self, filter: MessageFilterChain):
        self.filterChains.append(filter)

    def initializeVideoTransmitter(self) -> VideoTransmitter:
        if self.projectConfig.videoConfigs is None:
            raise Exception("Streamer configs not supported")
        videoTransmitter = createVideoTransmitter(**self.projectConfig.videoConfigs)
        videoTransmitter.setCredentials(self.projectConfig.credentials)
        self.transmitter = videoTransmitter
        return videoTransmitter

    def initializeIOTWrapper(self):
        clients = list()
        for clientPath in self.projectConfig.clientCredentialsPath:
            path = os.path.abspath(clientPath)
            config = {
                "server": "localhost",
                "httpPort": 5001,
                "tcpPort": 8000,
                "useSSL": False,
                "file": path
            }
            def onReceive(message):
                for filter in self.filterChains:
                    output = filter.doFilter(message)
                    if output is not None:
                        message = output

            client = IOTClientWrapper(self.projectConfig.token, config=config)
            client.set_on_receive(onReceive)
            clients.append(client)
        self.clients = clients
        return clients

def loadConfig(config):
    if not os.path.isabs(config):
        config = os.path.abspath(config)
        print(config)
    with open(config, "r") as file:
        data = load(file, Loader)
    config = ProjectConfig(controlnetConfig=config, **data)
    return config

if __name__ == "__main__":
    initializer = Initializer("../../config/iorConfigs.config")
    # videoTransmitter = initializer.initializeVideoTransmitter()
    # videoTransmitter.openBrowserAndHitLink()
    # while videoTransmitter.checkBrowserAlive():
    #     time.sleep(1)

    client1, client2 = initializer.initializeIOTWrapper()
    client1.start()
    # client2.start()

    while True:
        client1.sendMessage(message="Hello")
        time.sleep(1)

