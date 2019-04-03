import threading, time, requests,json,socket,os
import datetime

class IOTClient(threading.Thread):
    #__server = "192.168.1.7"
    __server = "192.168.1.10"
    __port = 8000
    def __init__(self,code,token,to,time_delay,debug=False,on_close = None,save_logs=False):
        threading.Thread.__init__(self)
        self.__code = code
        self.__token = token
        self.__to = to
        self.__time_delay = time_delay
        self.debug = debug
        self.__on_close = on_close
        self.__save_logs = save_logs
        self.__lock = threading.Lock()
        self.__isClosed = False

        self.__writeline("*" * 80)
        self.__writeline("Server Configuration IP: %s:%d" % (self.__server, self.__port))
        self.__writeline("User Token %s" % self.__token)
        self.__writeline("From Code: %d    To Code: %d" % (self.__code, self.__to))
        self.__writeline("Time Delay(in Seconds): %d" % self.__time_delay)
        self.__writeline("*" * 80)
        if not os.path.exists('./logs') and save_logs == True:
            os.mkdir('./logs')
        self.reconnect()

    def reconnect(self):
        r = requests.get('http://%s:8083/IOT-Beta/dashboard/socket/subscribe/%s/%d' % (self.__server, self.__token, self.__code))
        if r.status_code == 200:
            print("Request Successfully made to Server")

        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((self.__server, self.__port))

        self.__writeline("Connected to Socket Server")

        thread_0 = threading.Thread(target=self.__sendThread)
        thread_0.start()

    def __sendThread(self):
        time.sleep(10)
        self.__isClosed = False
        self.__writeline("Starting Heartbeat Thread")
        while not self.__isClosed:
            self.sendMessage("<HEARTBEAT>")
            time.sleep(self.__time_delay)

    def set_on_receive(self,fn):
        self.on_receive = fn

    def __writeline(self,msg):
        if self.debug:
            print(msg)

    def sendMessage(self,message,metadata = None):
        if self.__isClosed:
            return None
        try:
            msg = dict()
            msg["from"] = self.__code
            msg["token"] = self.__token
            if message == "<HEARTBEAT>":
                msg["to"] = [0]
                metadata = None
            else:
                msg["to"] = [0, self.__to]

            msg["message"] = message
            if metadata is not None:
                msg["syncData"] = metadata
            data = json.dumps(msg)

            self.__lock.acquire()

            #self.__s.send(b"<START>")
            self.__s.send(("%s\r\n"%data).encode())
            #self.__s.send(b"<END>")
            self.__writeline("Sending Message:")
            self.__writeline(data)
            self.time_start = time.time()*1000
        finally:
            self.__lock.release()

    def close(self):
        self.__s.shutdown(1)
        self.__s.close()
        self.__isClosed = True

        self.__writeline("Socket Closed")
        if self.__on_close != None:
            self.__on_close()

    def readData(self):
        if self.__isClosed:
            return None
        """
        dataString = ""
        try:
            char = self.__s.recv(1)
            dataString += char.decode()
        except socket.timeout:
            return None


        try:
            while True:
                char = self.__s.recv(1)
                if dataString.__contains__("\n") or char == b"":
                    break;
                dataString += char.decode()
            #dataString = json.loads(dataString[7+dataString.index("<START>"):dataString.index("<END")])
            if "message" in dataString:
                if dataString["message"] == "<RECOGNISED>" and dataString["status"] == "Connected":
                    self.__writeline(dataString)
                    dataString = None
        except ValueError:
            dataString = None
        """
        file_descriptor = self.__s.makefile('r')
        dataString = file_descriptor.readline()
        return json.loads(dataString)

    def run(self):
        print("Starting Thread")
        self.sendMessage("<INITIALMESSAGE>")
        while True:
            try:
                msg = self.readData()
                if msg is not None:
                    self.__writeline("Message Received:")
                    self.__writeline(msg)
                    try:
                        self.on_receive(msg)
                    except Exception as ex:
                        print("Error Occured while invoking Receive Function")
                        self.__writeline(ex)
            except socket.timeout:
                print("socket timeout")
            except ConnectionAbortedError as cae:
                print("Error Occured!!!")
                print(cae)
                break;
            time.sleep(0.01)
        print("Thread Terminated")
        self.close()


