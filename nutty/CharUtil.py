import asyncio
import readchar
from MavVehicle import MyQuad
import threading

class MyStatics:
    loop = None
class CharOperation:

    def __init__(self) -> None:
        self.armed = False
        self.mode = ""
        self.quad = MyQuad()
        self.runner = True
        
        # self.quad.setParameter("RC_OVERRIDE_TIME",10)

    async def startRun(self):
        while self.runner:
            await asyncio.sleep(.05)
        print("loop ended")

    def stopRun(self):
        self.runner = False

    async def startInit(self):
        await self.quad.init()    
    def throttleUP(self):
        self.quad.increaseThrottle()
    def throttleDown(self):
        self.quad.decreseThrottle()
    def yawLeft(self):
        self.quad.decreaseYaw()
    def yawRight(self):
        self.quad.increaseYaw()
    def pitchUp(self):
        self.quad.decreasePitch()
    def pitchDown(self):
        self.quad.increasePitch()
    def rollRight(self):
        self.quad.increaseRoll()
    def rollLeft(self):
        self.quad.decreaseRoll()
    async def arm(self):
        await self.quad.arm()
    async def disarmClose(self):
        await self.quad.disarm()
        await self.quad.close()
    def stabilizeMode(self):
        pass
    def altMode(self):
        pass
    def landMode(self):
        pass
    def positionMode(self):
        pass
    def defltThrot(self):
        self.quad.setDefaultToAll()
    def defltYaw(self):
        self.quad.setDefaultToAll()
    def defltPitch(self):
        self.quad.setDefaultToAll()
    def defltRoll(self):
        self.quad.setDefaultToAll()
    async def startManualControl(self):
        await self.quad.startManualControl()
    def stopManualControl(self):
        self.quad.stopManualControl()
    def changeThrottle(self,value):
        self.quad.changeThrottle(value)
    
    def kill(self):
        asyncio.ensure_future(self.quad.kill())
    def reboot(self):
        asyncio.ensure_future(self.quad.reboot())

    def shutdown(self):
        asyncio.ensure_future(self.quad.shutdown())

    def terminate(self):
        asyncio.ensure_future(self.quad.terminate())
    def calibrate(self):
        asyncio.ensure_future(self.quad.calibrate())
    
    def getQuad(self):
        return self.quad
    
class CharHandler:
    wait = True 
    def __init__(self,operations: CharOperation,startCap,stopCap) -> None:
        self.ops = operations
        self.startCap = startCap
        self.stopCap = stopCap

    def run(self):
        asyncio.set_event_loop(MyStatics.loop)
        asyncio.ensure_future(self.ops.startInit())
        while(self.wait):
            inp = readchar.readkey()

            if(inp == '\x1b[A'):
                print("up")
                self.ops.throttleUP()
            elif inp == '\x1b[B':
                print("Down")
                self.ops.throttleDown()
            elif inp == '\x1b[C':
                print("Right")
                self.ops.yawRight()
            elif inp == '\x1b[D':
                print("Left")
                self.ops.yawLeft()
            elif inp == '\x1b\x1b':
                print("Esc")
                asyncio.ensure_future(self.ops.disarmClose())
            elif inp == ' ':
                print("Space")
                asyncio.ensure_future(self.ops.arm())
            elif inp == 'w':
                print("W")
                self.ops.pitchUp()
            elif inp == 's':
                print("s")
                self.ops.pitchDown()
            elif inp == 'a':
                print("a")
                self.ops.rollRight()
            elif inp == 'd':
                print("D")
                self.ops.rollLeft()
            elif inp == '1':
                print("1")
                self.ops.changeThrottle(0.1)
                # self.ops.stabilizeMode()
            elif inp == '2':
                print("2")
                self.ops.changeThrottle(0.2)
                # self.ops.altMode()
            elif inp == '3':
                print("3")
                self.ops.changeThrottle(0.3)
                # self.ops.positionMode()
            elif inp == '0':
                print("calibration")
                self.ops.calibrate()
                # self.ops.landMode()
                
            elif inp == '4':
                print("4")
                self.ops.changeThrottle(0.4)
                # self.ops.landMode()
                
            elif inp == '5':
                print("5")
                self.ops.changeThrottle(0.5)
                # self.ops.landMode()
                
            elif inp == '6':
                print("6")
                self.ops.changeThrottle(0.6)
                # self.ops.landMode()
                
            elif inp == '7':
                print("7")
                self.ops.changeThrottle(0.7)
                # self.ops.landMode()
                
            elif inp == '8':
                print("8")
                self.ops.changeThrottle(0.8)
                # self.ops.landMode()
                
            elif inp == '\x16':
                self.ops.stopRun()
                self.wait = False
                break
            elif inp == '\x14':
                print("defaultTrot")
                self.ops.defltThrot()
            elif inp == '\x19':
                print("defaultYaw")
                self.ops.defltYaw()
            elif inp == '\x10':
                print("defaultPitch")
                self.ops.defltPitch()
            elif inp == '\x12':
                print("defaultRoll")
                self.ops.defltRoll()
            elif inp == 'g':
                print("startManual")
                asyncio.ensure_future(self.ops.startManualControl())
            elif inp == 'h':
                print("stopManual")
                self.ops.stopManualControl()
            elif inp == 'x':
                print("shutdown")
                self.ops.shutdown()
            elif inp == 'r':
                print("reboot")
                self.ops.reboot()
            elif inp == 'k':
                print("kill")
                self.ops.kill()
            elif inp == 't':
                print("terminate")
                self.ops.terminate()
            elif inp == '\x0c':
                print("start detecting")
                self.startCap()
            elif inp == '\x0b':
                print("stop detecting")
                self.stopCap()
            else:
                print(repr(inp))
            
            
# def runMain():
#     loop = asyncio.get_event_loop()
#     MyStatics.loop = loop
#     ops = CharOperation()
#     hand = CharHandler(ops)
#     threading.Thread(target=hand.run).start()
#     foo = loop.run_until_complete(ops.startRun())