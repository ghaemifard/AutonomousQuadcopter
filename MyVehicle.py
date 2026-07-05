
from mimetypes import init
from select import select
from matplotlib.pyplot import cla
from pymavlink import mavutil
import threading
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative

class MyQuad: 
    def PX4setMode(self,mavMode):
        self.drone1._master.mav.command_long_send(self.drone1._master.target_system, self.drone1._master.target_component,
                                               mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                               mavMode,
                                               0, 0, 0, 0, 0, 0)
    def __init__(self,connection) -> None:
        print(f"connecting to {connection}")
        self.drone1 = connect(connection,wait_ready=False)
        # self.drone1.wait_ready(True,timeout=200)
        self.running = True
        # threading.Thread(target=self.waitToClose,args=()).start()
    
    def waitToClose(self):
        while self.running:
            time.sleep(1)
    # def init(self,connection):
    #     drone = connect(connect,wait_ready=True)

    def arm(self):
        self.drone1.armed = True
        while not self.drone1.armed:
            time.sleep(1)
    
    def disarm(self):
        self.drone1.armed = False
        while self.drone1.armed:
            time.sleep(1)
    
    def closeDrone(self):
        self.running = False
        self.drone1.close()

    def setChannel(self,channel,value):
        self.drone1.channels.overrides[f'{channel}'] = int(value)

    
    def changeYaw(self,value):
        self.setChannel(4,value)
    
    def changeThrottle(self,value):
        self.setChannel(3,value)

    def changePitch(self,value):
        self.setChannel(2,value)

    def changeRoll(self,value):
        self.setChannel(1,value)

    
    def readCurrentChannel(self,channel):
        res = self.drone1.channels.overrides[f'{channel}']
        if res is None:
            res = self.drone1.channels[f'{channel}']
        return  res

    def increaseYaw(self):
        res = self.readCurrentChannel(4)
        if res is not None:
            self.changeYaw(res+25)
        else:
            print("cant get current value of yaw")
        return res
            
        

    def decreaseYaw(self):
        res = self.readCurrentChannel(4)
        if res is not None:
            self.changeYaw(res-25)
        else:
            print("cant get current value of yaw")
        return res
            
        

    def increaseThrottle(self):
        res = self.readCurrentChannel(3)
        if res is not None:
            self.changeThrottle(res+50)
        else:
            print("cant get current value of Throttle")
        return res

    def decreaseThrottle(self):
        res = self.readCurrentChannel(3)
        if res is not None:
            self.changeThrottle(res-50)
        else:
            print("cant get current value of Throttle")
        return res

    def increasePitch(self):
        res = self.readCurrentChannel(2)
        if res is not None:
            self.changeThrottle(res+25)
        else:
            print("cant get current value of Pitch")
        return res

    def decreasePitch(self):
        res = self.readCurrentChannel(2)
        if res is not None:
            self.changeThrottle(res-25)
        else:
            print("cant get current value of Pitch")
        return res

    def increaseRoll(self):
        res = self.readCurrentChannel(1)
        if res is not None:
            self.changeThrottle(res+25)
        else:
            print("cant get current value of Roll")
        return res

    def decreaseRoll(self):
        res = self.readCurrentChannel(1)
        if res is not None:
            self.changeThrottle(res-25)
        else:
            print("cant get current value of Roll")
        return res


            

    def setDefaultThrottle(self):
        self.changeThrottle(1000)

    def setDefaultYaw(self):
        self.changeYaw(1500)

    def setDefaultPitch(self):
        self.changePitch(1500)

    def setDefaultRoll(self):
        self.changeRoll(1500)
            
    def setStablizeMode(self):
        self.drone1.mode = VehicleMode("STABILIZE")

    def setLandMode(self):
        self.drone1.mode = VehicleMode("LAND")

    def setParameter(self,param,value):
        self.drone1.parameters[param] = value

    def getParameter(self,param):
        return self.drone1.parameters[param]

    def printParams(self):
        for k,v in self.drone1.parameters.items():
            print(f"{k}: {v}")

    def leftYaw(self,num):
        self.setDefaultYaw()
        for i in range(num):
            self.decreaseYaw()

    def rightYaw(self,num):
        self.setDefaultYaw()
        for i in range(num):
            self.increaseYaw()