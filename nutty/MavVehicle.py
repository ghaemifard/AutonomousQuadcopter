from ast import Not
import asyncio
import random
from threading import Thread
from mavsdk import System
import readchar
import threading

class QuadValue:
    def __init__(self) -> None:
        self.yaw = float(0)
        self.throttle = float(0)
        self.roll = float(0)
        self.pitch = float(0)

    def changeYaw(self,value):
        if(value < 1 and value > -1):
            self.yaw = value
        
class MyQuad:
    def __init__(self) -> None:
        self.drone = System()
        self.yaw = float(0.0)
        self.throttle = float(0.5)
        self.pitch = float(0.0)
        self.roll = float(0.0)
        self.runnung = False

    async def init(self):
        # await drone.connect(system_address=con)
        await self.drone.connect(system_address="serial:///dev/ttyACM0")
        print("Waiting for drone to connect...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break

    async def arm(self):
        await self.drone.manual_control.set_manual_control_input(
                float(self.roll), float(self.pitch), float(self.throttle), float(self.yaw)
            )
        await self.drone.action.arm()
    async def disarm(self):
        self.stopManualControl()
        await self.drone.action.disarm()

    async def sendManualData(self):
        on = False
        while self.runnung:
            # on = not on
            # diff = float(0)
            # if(on):
            #     diff = float(0.005)
            res = await self.drone.manual_control.set_manual_control_input(
                float(self.roll), float(self.pitch), float(self.throttle), float(self.yaw)
            )
            
            
            await asyncio.sleep(.07)
    async def startManualControl(self):
        self.runnung = True
        await self.sendManualData()

    def stopManualControl(self):
        self.runnung = False
    
    def increaseThrottle(self):
        if self.throttle <1:
            self.throttle += 0.05
        self.showStatus()

    def decreseThrottle(self):
        if(self.throttle>0):
            self.throttle -=  0.05
        self.showStatus()

    def increaseYaw(self):
        if(self.yaw<1):
            self.yaw +=  0.1
        self.showStatus()
         
    def decreaseYaw(self):
        if(self.yaw>-1):
            self.yaw -=  0.1
        self.showStatus()
         
    def increaseRoll(self):
        if(self.roll<1):
            self.roll +=  0.1
        self.showStatus()
         
    def decreaseRoll(self):
        if(self.roll>-1):
            self.roll -=  0.1
        self.showStatus()
         
    def increasePitch(self):
        if(self.pitch<1):
            self.pitch +=  0.1
        self.showStatus()
         
    def decreasePitch(self):
        if(self.pitch>-1):
            self.pitch -=  0.1
        self.showStatus()
         
    def showStatus(self):
        print(f"Roll:{self.roll} Pitch:{self.pitch} Throttle:{self.throttle} Yaw:{self.yaw}")

    async def close(self):
        await self.drone.action.kill()

    async def landMode(self):
        await self.drone.action.land()
    
    async def holdMode(self):
        await self.drone.action.hold()
    
    def changeThrottle(self,value):
        self.throttle = float(value)
    
    def setDefaultToAll(self):
        print("Default all")
        self.yaw = 0
        self.throttle = 0.2
        self.pitch = 0
        self.roll = 0

    def leftYaw(self,num):
        self.yaw = 0
        for _ in range(num):
            self.decreaseYaw()

    def rightYaw(self,num):
        self.yaw = 0
        for _ in range(num):
            self.increaseYaw()

    async def kill(self):
        await self.drone.action.kill()

    async def terminate(self):
        await self.drone.action.terminate()

    async def reboot(self):
        await self.drone.action.reboot()

    async def shutdown(self):
        await self.drone.action.shutdown()
    async def calibrate(self):
        await self.drone.calibration.calibrate_gyro()
        await self.drone.calibration.calibrate_level_horizon()


    