from json import JSONEncoder

class SocketMessage(JSONEncoder):
    """
    Message Model for Control Net Architecture.
    """
    def __init__(self, message=None, **d):
        JSONEncoder.__init__(self,**d)
        self.id = ""
        self.message = message
        self.status = ""
        self.syncData = dict()

    def default(self, o):
        obj = o.__dict__
        del obj['skipkeys']
        del obj['ensure_ascii']
        del obj['check_circular']
        del obj['allow_nan']
        del obj['sort_keys']
        del obj['indent']
        return obj