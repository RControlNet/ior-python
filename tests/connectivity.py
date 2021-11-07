import unittest
import time
from ior_research.utils.initializers import Initializer

count = 0
N_COUNT = 10

def onReceive(message):
    global count
    count += 1

class TestConnection(unittest.TestCase):

    def test_connection(self):
        self.initializer = Initializer("../config/iorConfigs.config")
        client1, client2 = self.initializer.initializeIOTWrapper("localhost")

        client1.set_on_receive(onReceive)
        client2.set_on_receive(onReceive)

        client1.start()
        client2.start()

        time.sleep(2)

        self.assertTrue(client1.client.connected, "Client 1 Not Connected to Server")
        self.assertTrue(client2.client.connected, "Client 2 Not Connected to Server")

        for i in range(N_COUNT):
            client1.sendMessage(message="Hello")
            time.sleep(1)
        time.sleep(1)

        self.assertEqual(N_COUNT+1, count, "COUNT NOT Received")

        client1.terminate()
        client2.terminate()

if __name__ == "__main__":
    unittest.main()