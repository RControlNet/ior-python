from yaml import load, Loader
from ior_research.IOTClient import IOTClientWrapper
import os, time

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

    def initializeVideoTransmitter(self) -> VideoTransmitter:
        if self.projectConfig.videoConfigs is None:
            raise Exception("Streamer configs not supported")
        videoTransmitter = createVideoTransmitter(**self.projectConfig.videoConfigs)
        videoTransmitter.setCredentials(self.projectConfig.credentials)
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

            client = IOTClientWrapper(self.projectConfig.token, config=config)
            clients.append(client)
        return clients

def loadConfig(config):
    if not os.path.isabs(config):
        config = os.path.abspath(config)
        print(config)
    with open(config, "r") as file:
        data = load(file, Loader)
    config = ProjectConfig(controlnetConfig=config, **data)
    return config


def on_receive(x):
    """Create a Receive message function, that takes a dict object"""
    print(x)

if __name__ == "__main__":
    initializer = Initializer("../../config/iorConfigs.config")
    videoTransmitter = initializer.initializeVideoTransmitter()
    videoTransmitter.openBrowserAndHitLink()
    while videoTransmitter.checkBrowserAlive():
        time.sleep(1)