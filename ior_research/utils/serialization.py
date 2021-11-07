import json

class PlainSerializer:
    def serialize(self, data):
        return data

class PlainDeserializer:
    def deserialize(self, data):
        return data

class JSONSerializer(PlainSerializer):
    def serialize(self, data):
        return json.dumps(data)

class JSONDeserializer(PlainDeserializer):
    def deserialize(self, data):
        return json.loads(data)