import requests
from ior_research.utils import consts

class IORHttpClient:
    def __init__(self, server = None):
        if server is None:
            server = consts.TUNNEL_SERVER + "/api"
        self.server = server
        self.token = None
        self.verify = False

    def fetchToken(self, username, password):
        response = requests.post(self.server + "/refreshToken", json = {
            "username": username,
            "password": password
        }, headers ={
            "content-type": "application/json"
        }, verify= self.verify)
        self.token = response.json()['jwt']