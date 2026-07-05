import asyncio
import readchar
from MavVehicle import MyQuad
import threading
import time
from MyStatistics import MyStatics
class CharOperation:

    def __init__(self) -> None:
        self.armed = False
        self.mode = ""
        self.quad = MyQuad()
        self.runner = True
        
        # self.quad.setParameter("RC_OVERRIDE_TIME",10)

    async def startRun(self):
        while self.runner:
            await asyncio.sleep(.02)
        print("loop ended")

    def stopRun(self):
        self.runner = False

    async def startInit(self):
        await self.quad.init()    
    async def throttleUP(self):
        await self.quad.increaseThrottle()
    async def throttleDown(self):
        await self.quad.decreseThrottle()
    async def yawLeft(self):
        await self.quad.decreaseYaw()
    async def yawRight(self):
        await self.quad.increaseYaw()
    async def pitchUp(self):
        await self.quad.decreasePitch()
    async def pitchDown(self):
        await self.quad.increasePitch()
    async def rollRight(self):
        await self.quad.increaseRoll()
    async def rollLeft(self):
        await self.quad.decreaseRoll()
    async def arm(self):
        await self.quad.arm()
    async def disarmClose(self):
        await self.quad.disarm()
        await self.quad.close()
    def stabilizeMode(self):
        pass
    def altMode(self):
        pass
    def holdMode(self):
        asyncio.ensure_future(self.quad.holdMode())
    def landMode(self):
        asyncio.ensure_future(self.quad.landMode())
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
        # self.quad.changeThrottle(value)
        asyncio.ensure_future(self.quad.health())
    
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
    def printDistance(self):
        asyncio.ensure_future(self.quad.printDistance())
    
    def getQuad(self):
        return self.quad

    def nCommand(self):
        asyncio.ensure_future(self.quad.nCommand())
    
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
                print("up\r\n")
                asyncio.ensure_future(self.ops.throttleUP())
            elif inp == '\x1b[B':
                print("Down\r\n")
                asyncio.ensure_future(self.ops.throttleDown())
            elif inp == '\x1b[C':
                print("Right\r\n")
                asyncio.ensure_future(self.ops.yawRight())
            elif inp == '\x1b[D':
                print("Left\r\n")
                asyncio.ensure_future(self.ops.yawLeft())
            elif inp == '\x1b\x1b':
                print("Esc")
                asyncio.ensure_future(self.ops.disarmClose())
            elif inp == ' ':
                print("Space\r\n")
                asyncio.ensure_future(self.ops.arm())
            elif inp == 'w':
                print("W\r\n")
                asyncio.ensure_future(self.ops.pitchUp())
            elif inp == 's':
                print("s\r\n")
                asyncio.ensure_future(self.ops.pitchDown())
            elif inp == 'd':
                print("d\r\n")
                asyncio.ensure_future(self.ops.rollRight())
            elif inp == 'a':
                print("a\r\n")
                asyncio.ensure_future(self.ops.rollLeft())
            elif inp == '1':
                print("1")
                threading.Thread(target=lambda:MyStatics().makePitchForseconds(3)).start()
                # self.ops.stabilizeMode()
            elif inp == '2':
                print("2")
                self.ops.changeThrottle(20)
                # self.ops.altMode()
            elif inp == '3':
                print("3")
                self.ops.changeThrottle(30)
                # self.ops.positionMode()
            elif inp == '0':
                print("calibration\r\n")
                self.ops.calibrate()
                # self.ops.landMode()
                
            elif inp == '4':
                print("4")
                self.ops.holdMode()
                # self.ops.landMode()
                
            elif inp == '5':
                print("5")
                # self.ops.changeThrottle(50)
                self.ops.landMode()
                
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
                print("shutdown\r\n")
                self.ops.shutdown()
            elif inp == 'r':
                print("reboot\r\n")
                self.ops.reboot()
            elif inp == 'k':
                print("kill\r\n")
                self.ops.kill()
            elif inp == 't':
                print("terminate\r\n")
                self.ops.terminate()

            elif inp == 'm':
                print("printDistance\r\n")
                MyStatics.myM = not MyStatics.myM
                if(MyStatics.myM):
                    print("Starting mmmmmmmmmmmmm\r\n")
                else:
                    print("STOPPPPPPP mmmmmmmmmmmmm\r\n")
                self.ops.printDistance()

            elif inp == 'n':
                self.ops.nCommand()
            elif inp == '\x0c':
                print("start detecting\r\n")
                self.startCap()
            elif inp == '\x0b':
                print("stop detecting\r\n")
                MyStatics.recording = False
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