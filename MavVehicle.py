import asyncio
import random
from threading import Thread
from mavsdk import System
import readchar
import threading
class MyQuad:
    def __init__(self) -> None:
        self.drone = System()
        self.yaw = float(0.0)
        self.throttle = float(0.4)
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
        await self.drone.action.arm()
    async def disarm(self):
        self.stopManualControl()
        await self.drone.action.disarm()

    async def sendManualData(self):
        while self.runnung:
            await self.drone.manual_control.set_manual_control_input(
                float(self.roll), float(self.pitch), float(self.throttle), float(self.yaw)
            )
            await asyncio.sleep(.1)
    async def startManualControl(self):
        self.runnung = True
        
        await self.sendManualData()
    def stopManualControl(self):
        self.runnung = False
    
    def increaseThrottle(self):
        if self.throttle <1:
            self.throttle += 0.025
        self.showStatus()
    def decreseThrottle(self):
        if(self.throttle>0):
            self.throttle -=  0.025
        self.showStatus()

    def increaseYaw(self):
        if(self.yaw<1):
            self.yaw +=  0.025
        self.showStatus()
         
    def decreaseYaw(self):
        if(self.yaw>-1):
            self.yaw -=  0.025
        self.showStatus()
         
    def increaseRoll(self):
        if(self.roll<1):
            self.roll +=  0.025
        self.showStatus()
         
    def decreaseRoll(self):
        if(self.roll>-1):
            self.roll -=  0.025
        self.showStatus()
         
    def increasePitch(self):
        if(self.pitch<1):
            self.pitch +=  0.025
        self.showStatus()
         
    def decreasePitch(self):
        if(self.pitch>-1):
            self.pitch -=  0.025
        self.showStatus()
         
    def showStatus(self):
        print(f"Throttle:{self.throttle} Yaw:{self.yaw} Pitch:{self.pitch} Roll:{self.roll}")

    async def close(self):
        await self.drone.action.kill()

    async def landMode(self):
        await self.drone.action.land()
    
    async def holdMode(self):
        await self.drone.action.hold()

    