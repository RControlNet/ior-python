# from ior_research import IOTClient
# import time
#
# class Transmitter(IOTClient):
#     def __init__(self,code,token,to,debug=False,server='iorcloud.ml'):
#         IOTClient.__init__(self,code,token,to,isTunneled=True,debug=debug,server=server)
#         assert self.connected, "Could not connect to %s"%server
#         self.receiver_connected = False
#
#     def waitForReceiver(self):
#         while not self.receiver_connected:
#             if self.file.readable():
#                 data = self.readData()
#                 if data['message'] ==  "100":
#                     self.receiver_connected = True
#                     self._writeline("Client Connected")
#             time.sleep(0.5)
#
#     def sendData(self,data):
#         assert self.receiver_connected, "Receiver is not connected"
#         self.file.write(data)
#         self.file.flush()
#
#     def run(self):
#         assert self.connected, "Server not connected"
#         while self.file.readable():
#             data = self.readData()
#             if data["message"] == "250":
#                 self._writeline("Connection to the other side is broken")
#                 self.receiver_connected = False
#                 break;
#             if data['message'] == "100":
#                 self.receiver_connected = True
