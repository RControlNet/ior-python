class SocketMessage:
    def __init__(self, message, status, **kwargs):
        self.message = message
        self.status = status
        self.syncData = kwargs['syncData']