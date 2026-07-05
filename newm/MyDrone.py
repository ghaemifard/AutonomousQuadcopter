
from ast import arg
from concurrent.futures import thread
from readline import parse_and_bind
import sys
from dronekit import connect,VehicleMode,Vehicle
import time
import threading


class Drone:
    connection_string = ":14550"
    instance = None
    def getInstance():
        if Drone.instance is None:
            Drone.instance = Drone()
        return Drone.instance
    def __init__(self) -> None:
        self.drone = connect(self.connection_string,True)
        self.roll = 1500
        self.pitch = 1500
        self.yaw = 1500
        self.throttle = 1000
        self.startedManual = False
        self.socketSend = None
        self.goJelou = False
        # self.drone.parameters.add_attribute_listener("chan6_raw",self.any_parameter_callback)
        self.drone.add_message_listener("RC_CHANNELS",self.any_parameter_callback)
        self.rc_override = False
    
    def printSocket(self,msg):
        if self.socketSend is not None:
            self.socketSend(msg)
    def startControlManual(self):
        if not self.startedManual:
            self.startedManual = True
            self.printSocket("Computer Control started")
            threading.Thread(target=self.runManual,args=()).start()

    def stopControlManual(self):
        self.startedManual = False
        self.printSocket("Computer Control Stopped")

    def arm(self):
        
        if self.drone.is_armable:
            self.drone.arm(True)
            self.printSocket("Armed")
        else:
            self.drone.armed = True
            time.sleep(1)
            if not self.drone.armed:
                print("drone is not armable\r\n")
                self.printSocket("drone is not armable")

    def disArm(self):
        self.stopControlManual()
        self.throttle = 1000
        self.drone.armed = False
        self.drone.disarm()
        self.printSocket("Disarmed")

    def stabilize(self):
        self.drone.mode = VehicleMode("STABILIZE")
        self.printSocket("Stabilize mode")
    def land(self):
        self.yaw = 1500
        self.pitch = 1500
        self.roll = 1500
        self.drone.mode = VehicleMode("LAND")
        self.printSocket("Land mode")

    def altHold(self):
        self.drone.mode = VehicleMode("ALT_HOLD")
        self.throttle = 1460
        self.printSocket("AltHold mode")

    def posHold(self):
        self.drone.mode = VehicleMode("POSHOLD")
        self.throttle = 1460
        self.printSocket("PosHold mode")

    def loiter(self):
        self.drone.mode = VehicleMode("LOITER")
        self.throttle = 1460
        self.printSocket("Loiter mode")

    def rtl(self):
        # self.drone.mode = VehicleMode("RETURN_TO_LAUNCH")
        self.drone.mode = VehicleMode("RTL")
        self.printSocket("RTL mode")

    def close(self):
        self.drone.close()
    def runManual(self):
        print("manual is runnning\r\n")
        while self.startedManual:
            self.drone.channels.overrides['1'] = int(self.roll)
            self.drone.channels.overrides['2'] = int(self.pitch)
            self.drone.channels.overrides['3'] = int(self.throttle)
            self.drone.channels.overrides['4'] = int(self.yaw)
            time.sleep(.1)

    def increaseThrottle(self):
        inc = 25
        if(self.throttle + inc < 1970):
            self.throttle += inc
        self.status()
    def decreaseThrottle(self):
        dec = 25
        if self.throttle - dec > 1020:
            self.throttle -= dec
        self.status()


    def increaseYaw(self,num=1):
        inc = 25 * num
        if(self.yaw + inc < 1970):
            self.yaw += inc
        self.status()
    def decreaseYaw(self,num=1):
        dec = 25 * num
        if self.yaw - dec > 1020:
            self.yaw -= dec
        self.status()


    def increaseRoll(self,num=1):
        inc = 25 * num
        if(self.roll + inc < 1970):
            self.roll += inc
        self.status()
    def decreaseRoll(self,num=1):
        dec = 25 * num
        if self.roll - dec > 1020:
            self.roll -= dec
        self.status()



    def increasePitch(self,num=1):
        inc = 25 * num
        if(self.pitch + inc < 1970):
            self.pitch += inc
        self.status()
    def decreasePitch(self,num=1):
        dec = 25 * num
        if self.pitch - dec > 1020:
            self.pitch -= dec
        self.status()

    def calibrateGyro(self):
        self.drone.send_calibrate_gyro() 
        self.printSocket("Gyro calibrated")

    def calibrateLevel(self):
        self.drone.send_calibrate_vehicle_level() 
        self.printSocket("Level Calibrated")
    def calibratePressure(self):
        self.drone.send_calibrate_barometer()
        self.printSocket("Pressure Calibrated")

    def killMe(self):
        self.drone.reboot()
        self.printSocket("Rebooted")

    def status(self):
        msg = f"roll: {self.roll} pitch: {self.pitch} throttle: {self.throttle} yaw: {self.yaw}\r\n"
        print(msg)
        self.printSocket(msg)

    def exitMe(self):
        threading.Thread(target=self.closeMe).start()
        self.printSocket("Exiting")
    def jelouSec(self,num):
        self.goJelou = True
        self.printSocket(f"sleeping for {num}")
        time.sleep(num)
        self.goJelou = False
        self.printSocket(f"Awake")
    def goForward(self):
        self.printSocket("GoF1")
        threading.Thread(target=self.jelouSec,args=(2,)).start()
    def closeMe(self):
        self.disArm()
        time.sleep(2)
        self.close()
        
    
    def any_parameter_callback(self,fake, attr_name, value):
        val = int(value.chan6_raw)
        if val>1900:
            self.rc_override = True
        else:
            self.rc_override = False

        print(f"RC_Override: {self.rc_override}\r\n")
        # print(" PARAMETER CALLBACK: %s changed to: %s" % (attr_name, value))