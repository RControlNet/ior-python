import importlib
from typing import List

import rcn
import os, time, sys
try:
    import ior_research
except ModuleNotFoundError:
    sys.path.append("../../")

from ior_research.utils.filterchains import MessageFilterChain
from ior_research.IOTClient import IOTClientWrapper
from ior_research.utils.video import VideoTransmitter, createVideoTransmitter
import logging
logger = logging.getLogger(__name__)

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
        self.credentials = kwargs['credentials']
        self.credentials = Credentials(**self.credentials)
        self.filters = kwargs['filters'] if 'filters' in kwargs else list()

class Initializer:
    def __init__(self, configPath):
        self.projectConfig = loadConfig(configPath)
        self.filterChains = []
        self.transmitter = None
        self.clients = []
        self.loadFilters()

    def loadFilters(self):
        for filterObj in self.projectConfig.filters:
            filter = filterObj.name
            module_elements = filter.split('.')
            module = importlib.import_module("."+module_elements[-2], '.'.join(module_elements[:-2]))
            print(module)
            if module_elements[-1] not in dir(module):
                logger.error(f"Filter class {module_elements[-1]}, Not found in module {'.'.join(module_elements[:-1])}")
                raise ImportError(f"Filter class {module_elements[-1]}, Not found in module {'.'.join(module_elements[:-1])}")
            classInstance = getattr(module, module_elements[-1])
            objInstance = classInstance(self, configuration=filterObj.configuration)
            self.filterChains.append(objInstance)
            print(self.filterChains)
            logger.info(f"Filter Loaded: {filter}")


    def addFilter(self, filter: MessageFilterChain):
        self.filterChains.append(filter)

    def initializeVideoTransmitter(self) -> VideoTransmitter:
        if self.projectConfig.videoConfigs is None:
            raise Exception("Streamer configs not supported")
        videoTransmitter = createVideoTransmitter(**self.projectConfig.streamer)
        videoTransmitter.setCredentials(self.projectConfig.credentials)
        self.transmitter = videoTransmitter
        return videoTransmitter

    def initializeIOTWrapper(self, server="localhost", httpPort=5001, tcpPort=8000) -> List[IOTClientWrapper]:
        clients = list()
        for clientPath in self.projectConfig.clientJson:
            path = os.path.abspath(clientPath)
            config = {
                "server": server,
                "httpPort": httpPort,
                "tcpPort": tcpPort,
                "useSSL": False,
                "file": path
            }

            def onReceive(message):
                for filter in self.filterChains:
                    print(message)
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
    # with open(config, "r") as file:
    #     data = load(file, Loader)
    data = rcn.utils.loadYamlAsClass(config)
    print(data)
    # config = ProjectConfig(controlnetConfig=config, **data)
    return data

if __name__ == "__main__":
    initializer = Initializer("../../config/iorConfigsFrom.yml")
    videoTransmitter = initializer.initializeVideoTransmitter()
    videoTransmitter.openBrowserAndHitLink()
    while videoTransmitter.checkBrowserAlive():
        time.sleep(1)

