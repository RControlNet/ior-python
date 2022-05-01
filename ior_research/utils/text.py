from marshmallow import Schema, fields, post_dump, post_load


class SocketMessage:
    def __init__(self, message, status=None, syncData=dict()):
        self.message = message
        self.status = status
        self.syncData=syncData


class SocketMessageSchema(Schema):
    message = fields.Str()
    status = fields.Str(required=False, default=None)
    syncData = fields.Dict(required=False, default=None)

    @post_load
    def parseObject(self, data, **kwargs):
        return SocketMessage(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        print(data)
        return dict(map(lambda key: (key,data[key]), filter(lambda key: data[key] is not None, data)))

socketMessageSchema = SocketMessageSchema()