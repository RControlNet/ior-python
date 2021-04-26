# from ior_research import IOTClient
# import time
#
# class Receiver(IOTClient):
#     def __init__(self,code,token,to,debug=False,server='iorcloud.ml'):
#         IOTClient.__init__(self,code,token,to,isTunneled=True,debug=debug,server=server)
#         assert self.connected, "Could not connect to %s"%server
#         self.transmitter_connected = False
#         self.onRequest = None
#
#     def setOnRequest(self,function):
#         if self.onRequest is not None:
#             self.onRequest.stop()
#
#         self.onRequest = RepeatedTimer(3,function)
#         self.onRequest.start()
#
#     def waitForTransmitter(self):
#         while not self.transmitter_connected:
#             if self.file.readable():
#                 data = self.readData()
#                 if data['message'] == "102":
#                     self.transmitter_connected = True
#                     self._writeline("Transmitter Connected")
#             time.sleep(0.5)
#
#     def run(self):
#         assert self.connected, "Server not connected"
#         while True:
#             if self.file.readable:
#                 data = self.readData()
#                 if data["message"] == "250":
#                     self._writeline("Connection to the other side is broken")
#                     self.transmitter_connected = False
#                     break;
#
#         if self.onRequest is not None:
#             self.onRequest.stop()
#
# from threading import Timer
#
# class RepeatedTimer(object):
#     def __init__(self, interval, function):
#         self._timer     = None
#         self.interval   = interval
#         self.function   = function
#
#         self.is_running = False
#         self.start()
#
#     def _run(self):
#         self.is_running = False
#         self.start()
#         self.function()
#
#     def start(self):
#         if not self.is_running:
#             self._timer = Timer(self.interval, self._run)
#             self._timer.start()
#             self.is_running = True
#
#     def stop(self):
#         self._timer.cancel()
#         self.is_running = False