from cndi.annotations import Bean
from paho.mqtt.client import Client

@Bean()
def getMqttClient() -> Client:
    return Client()