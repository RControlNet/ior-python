import requests

class IORHttpClient:
    def __init__(self, server):
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
