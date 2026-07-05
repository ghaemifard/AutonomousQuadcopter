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
        pass
    def defltYaw(self):
        pass
    def defltPitch(self):
        pass
    def defltRoll(self):
        pass
    async def startManualControl(self):
        await self.quad.startManualControl()
    def stopManualControl(self):
        self.quad.stopManualControl()


    
    
class CharHandler:
    wait = True
    def __init__(self,operations: CharOperation) -> None:
        self.ops = operations
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
                self.ops.stabilizeMode()
            elif inp == '2':
                print("2")
                self.ops.altMode()
            elif inp == '3':
                print("3")
                self.ops.positionMode()
            elif inp == '0':
                print("0")
                self.ops.landMode()
            elif inp == '\x03':
                self.ops.stopRun()
                self.wait = False
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
            
            


loop = asyncio.get_event_loop()
MyStatics.loop = loop
ops = CharOperation()
hand = CharHandler(ops)
threading.Thread(target=hand.run).start()
foo = loop.run_until_complete(ops.startRun())