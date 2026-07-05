
import threading
import socket
from time import time,sleep
from MyDrone import Drone

class MySocket:
    clientConnected = False
    instance = None
    
    def getInstance():
        if MySocket.instance is None:
            MySocket.instance = MySocket()
        return MySocket.instance

    def manageTime(self):
        while True:
            sleep(.5)
            if self.prevTime is not None:
                elapsed = time() - self.prevTime
                if elapsed > 1.5:
                    print("landing\r\n")
                    self.drone.land()
                    ################# do land
    def closeAll(self):
        MySocket.clientConnected = False
        print("Closing Connection")
        if self.clientSocket is not None:
            self.clientSocket.close()
        if self.socket is not None:
            self.socket.close()
        
    def __init__(self) -> None:
         
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        print("socker created")
        self.clientSocket = None
        self.clientAddr = None
        self.prevTime = None
        self.doCapture = None
        self.dontCapture = None
        threading.Thread(target=self.waitForConn).start()
        threading.Thread(target=self.manageTime).start()
        self.drone = Drone.getInstance() 
        self.drone.socketSend = self.printData
    
    def waitForConn(self):
        try:
            port = 4321
            print("socker binded and listening: before bind")
            self.socket.bind(('',port))
            print("socker binded and listening: before listen")
            self.socket.listen()
            print("socker binded and listening: before accept")
            self.clientSocket, self.clientAddr = self.socket.accept()
            MySocket.clientConnected = True
            threading.Thread(target=self.getData).start()
        except:
            self.closeAll()

    
    def getData(self):
        while MySocket.clientConnected:
            print("waiting for data")
            dat = self.clientSocket.recv(5)
            threading.Thread(target=self.handleData,args=(dat,)).start()
            
    def printData(self,data):
        if MySocket.clientConnected:
            data = str.encode(data)
            threading.Thread(target=self.clientSocket.send,args=(data,)).start()
    
    def handleData(self,data):
        
        try:
            data = data.decode("utf-8")
            if data is None or len(data) < 2:
                raise Exception("data is None")
        except:
            print("data is none")
            self.closeAll()
            return
        t0 = time()
        # elapsedTime = 0.0
        # if self.prevTime is not None:
        #     elapsedTime = t0 - self.prevTime
        data = str.strip(data)
        # self.printData(f"Got msg: {data} in between {elapsedTime}")
        self.prevTime = t0
        if data == 'a0':
            self.drone.increaseThrottle()
        elif data == 'a1':
            self.drone.decreaseThrottle()
        elif data == 'a2':
            self.drone.increaseYaw()
        elif data == 'a3':
            self.drone.decreaseYaw()
        elif data == 'a4':
            self.drone.decreasePitch()
        elif data == 'a5':
            self.drone.increasePitch()
        elif data == 'a6':
            self.drone.increaseRoll()
        elif data == 'a7':
            self.drone.decreaseRoll()
        elif data == 'a8':
            self.drone.exitMe()
            self.closeAll()
        elif data == 'a9':
            self.drone.startControlManual()
        elif data == 'b0':
            self.drone.stopControlManual()
        elif data == 'b1':
            self.drone.arm()
        elif data == 'b2':
            self.drone.stabilize()
        elif data == 'b3':
            self.drone.loiter()
        elif data == 'b4':
            self.drone.posHold()
        elif data == 'b5':
            self.drone.altHold()
        elif data == 'b6':
            self.drone.land()
        elif data == 'b7':
            self.drone.rtl()
        elif data == 'b8':
            self.doCapture()
        elif data == 'b9':
            self.dontCapture()
        elif data == 'c0':
            self.drone.calibrateGyro()
        elif data == 'c1':
            self.drone.calibrateLevel()
        elif data == 'c2':
            self.drone.killMe()
            self.closeAll()
        elif data == 'c3':
            self.drone.disArm()
        elif data == 'c4':
            self.drone.calibratePressure()
        elif data == 'c5':
            self.drone.goForward()
        elif data == 'c6':
            pass
        elif data == 'c7':
            pass
        elif data == 'c8':
            pass
        elif data == 'c9':
            pass
        else:
            print(f"{data} dosn't do anything!\r\n")
        






