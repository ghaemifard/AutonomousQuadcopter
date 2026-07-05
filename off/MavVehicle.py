from ast import Not
import asyncio
import random
from threading import Thread
from mavsdk import System
import readchar
import threading
from mavsdk.offboard import (Attitude, OffboardError)
from mavsdk.action import ActionError
from simple_pid import PID
import time
from MyStatistics import MyStatics

class QuadValue:
    def __init__(self) -> None:
        self.yaw = float(0)
        self.throttle = float(.5)
        self.roll = float(0)
        self.pitch = float(0)

    def changeYaw(self,value):
        if(value < 100 and value > -100):
            self.yaw = value
        
class MyQuad:
    def __init__(self) -> None:
        self.drone = System()
        self.yaw = float(-90.0)
        self.throttle = float(0.15)
        self.pitch = float(3.5)
        self.roll = float(3.0)

        self.pitch = float(0.0)
        self.roll = float(0.0)
        self.runnung = False 
        self.pid = PID(5, .4, .7) # Good 
        self.pid.setpoint = 100.0
        self.distance = 0
        self.prevTime = 0
        self.prevDist = 30

        self.MaxThrottle = 0.860

        self.curPitch = -100
        self.nCom = False
        self.distList = list()
        self.currentYaw = self.yaw

    async def init(self):
        # await drone.connect(system_address=con)
        # await self.drone.connect(system_address="serial:///dev/ttyACM0")
        await self.drone.connect(system_address="udp://:14550")
        print("Waiting for drone to connect...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break

    async def arm(self):
        # await self.drone.manual_control.set_manual_control_input(
        #         float(self.roll), float(self.pitch), float(self.throttle), float(self.yaw)
        #     )
        # await self.calibrate()
        await self.drone.action.arm()
        await self.drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.0))
        try:
            await self.drone.offboard.start()
        except OffboardError as error:
            print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
            print("-- Disarming")
            await self.drone.action.disarm()
            
    async def sendAttitute(self):
        await self.drone.offboard.set_attitude(Attitude(self.roll, self.pitch, self.yaw, self.throttle))
    async def disarm(self):
        self.stopManualControl()
        await self.drone.offboard.stop()
        try:
            await self.drone.action.disarm()
        except ActionError as e:
            print(e)

    async def sendManualData(self):
        on = False
    async def startManualControl(self):
        self.runnung = True
        # await self.sendManualData()

    def stopManualControl(self):
        self.runnung = False
    
    async def increaseThrottle(self,count = 1):
        baseValue = 0.01
        if MyStatics.myM:
            if(self.MaxThrottle<.9):
                self.MaxThrottle += baseValue * count
            print(f"Max Throttle: {self.MaxThrottle}")
            return
        
        if (baseValue > 0.65):
            baseValue = 0.005
        elif(self.throttle>0.70):
            baseValue = 0.002
        

        if self.throttle <.83:
            self.throttle += baseValue * count
            await self.sendAttitute()
        self.showStatus()
    
    async def trot(self,count = 1):
        if self.throttle < self.MaxThrottle:
            self.throttle += 0.01 * count
        else:
            self.throttle = self.MaxThrottle
        if(not MyStatics.recording):    
            await self.sendAttitute()
        self.showStatus()
        

    async def decreseThrottle(self,count = 1):
        baseValue = 0.01
        if MyStatics.myM:
            if(self.MaxThrottle>0):
                self.MaxThrottle -= baseValue * count

            print(f"Max Throttle: {self.MaxThrottle}")
            return
        

        if (baseValue > 0.65):
            baseValue = 0.005
        elif(self.throttle > 0.70):
            baseValue = 0.002
        


        if(self.throttle>0):
            self.throttle -=  baseValue * count
            await self.sendAttitute()
        self.showStatus()

    async def increaseYaw(self):
        if(self.yaw<10000):
            self.yaw +=  1
            await self.sendAttitute()
        self.showStatus()
         
    async def decreaseYaw(self):
        if(self.yaw>-10000):
            self.yaw -=  1
            await self.sendAttitute()
        self.showStatus()
         
    async def increaseRoll(self):
        if(self.roll<30):
            self.roll +=  .5
            await self.sendAttitute()
        self.showStatus()
         
    async def decreaseRoll(self):
        if(self.roll>-30):
            self.roll -=  .5
            await self.sendAttitute()
        self.showStatus()
         
    async def increasePitch(self):
        if(self.pitch<20):
            self.pitch +=  .5
            await self.sendAttitute()
        self.showStatus()
         
    async def decreasePitch(self):
        if(self.pitch>-20):
            self.pitch -=  .5
            await self.sendAttitute()
        self.showStatus()
         
    def showStatus(self):
        print(f"Roll:{self.roll} Pitch:{self.pitch} Throttle:{self.throttle} Yaw:{self.yaw}\r\n")

    async def close(self):
        await self.drone.action.kill()

    async def landMode(self):
        await self.drone.action.land()
    
    async def holdMode(self):
        await self.drone.action.hold()
    
    
    async def health(self):
        async for health in self.drone.telemetry.health():
            print(health)
    

    def changeThrottle(self,value):
        self.throttle = float(value)
    
    def setDefaultToAll(self):
        print("Default all")
        self.yaw = 0
        self.throttle = 0.4
        self.pitch = 0
        self.roll = 0

    def leftYaw(self,num):
        # self.yaw = 0
        # for _ in range(num):
        #     self.decreaseYaw()
        # asyncio.ensure_future(self.sendAttitute())
        diff = 1  * num
        if(self.yaw>-10000+diff):
            self.yaw -=  diff
            # print(f"yawL: {self.yaw}")
            asyncio.ensure_future(self.sendAttitute())

    def rightYaw(self,num):
        # self.yaw = 0
        # for _ in range(num):
        #     self.increaseYaw()
        # asyncio.ensure_future(self.sendAttitute())
        diff = 1  * num
        if(self.yaw<10000-diff):
            self.yaw +=  diff
            # print(f"yawR: {self.yaw}")
            asyncio.ensure_future(self.sendAttitute())

    async def kill(self):
        await self.drone.action.kill()

    async def terminate(self):
        await self.drone.action.terminate()

    async def reboot(self):
        await self.drone.action.reboot()

    async def shutdown(self):
        await self.drone.action.shutdown()
    async def calibrate(self):
        async for gy in self.drone.calibration.calibrate_gyro():
            print(gy)
        print("Gyro finished\r\n")
        # async for gy in  self.drone.calibration.calibrate_level_horizon():
        #     print(gy)
        # print("level finished")


    def goForward(self):
        if(self.curPitch == -100):
            self.curPitch = self.pitch
        self.pitch = self.curPitch + 2.0
    def goBackward(self):
        if(self.curPitch == -100):
            self.curPitch = self.pitch
        self.pitch = self.curPitch - 2.0

    def stopPitch(self):
        if(self.curPitch != -100):
            self.pitch = self.curPitch
        self.curPitch = -100

    async def nCommand(self):
        if(self.nCom):
            return
        self.nCom = True
        distance = self.distance
        print(f"keeping distance of {distance}")
        while True:
            await asyncio.sleep(1)
            if(not MyStatics.myM):
                break
            self.distList.append(self.distance)
            if(self.isChangedDisrection()):
                await asyncio.sleep(4)
                continue
            if(self.distance < distance - 10):
                print(f"New Distance: {self.distance} compare to Original: {distance}")
                await self.increaseThrottle(1)
            else:
                print(f"self distance:{self.distance} and distance:{distance}")

        self.nCom = False    

    async def controlHeight(self):

        await self.trot(1)

        # t0 = time.time()
        # if (t0-self.prevTime < .1):
        #     return
        # distance = self.pid(self.distance)
        # self.prevTime = t0
        # print(f"realDis: {self.distance} and pidDist: {distance}\r\n")

        # if distance < 0.0:
        #     await self.decreseThrottle(.1)
        # else:
        #     await self.increaseThrottle(.1)

        

    def isChangedDisrection(self):
        if(len(self.distList) > 2):
            bl0 = self.distList[-2]<self.distList[-3]
            bl1 = self.distList[-1]<self.distList[-2]
            if bl0 != bl1:
                return True
        return False
    async def printDistance(self):
        async for dis in self.drone.telemetry.distance_sensor():
            # print(f"Distance: {dis.current_distance_m}\r\n")
            # continue
            if(not MyStatics.myM):
                return
            
            # if(dis.current_distance_m >0 and dis.current_di÷stance_m < 250 and dis.current_distance_m != 30.0 ) or True :  #and abs(self.prevDist-dis.current_distance_m)<130)
            if(dis.current_distance_m >0  ) :  #and abs(self.prevDist-dis.current_distance_m)<130)
                # d = (self.pid(dis.current_distance_m))
                
                # self.distance = d
                self.distance = dis.current_distance_m
                # self.distList.append(dis.current_distance_m)
                await self.controlHeight()
                self.prevTime = self.distance
            # await asyncio.sleep(0.1)
            
            

    
    
    # async def holdMode(self):
    #     await self.drone.action.hold()
    
    
    # async def landMode(self):
    #     await self.drone.action.land()
    


    