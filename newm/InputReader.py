from select import select
import threading
from time import time,sleep
from pip import main
import readchar
from MyDrone import Drone
class MyConsole:
    instance = None
    def getInstance():
        if MyConsole.instance is None:
            MyConsole.instance = MyConsole()
        return MyConsole.instance
    def __init__(self) -> None:
        self.started = False
        self.drone = Drone.getInstance()
        self.doCapture = None
        self.dontCapture = None


    def startConsole(self):
        self.started = True
        threading.Thread(target=self.run,args=()).start()

    def stopConsole(self):
        self.started = False

    
    def run(self):
        while(self.started):
            inp = readchar.readkey()
            if(inp == '\x1b[A'):
                print("up\r\n")
                self.drone.increaseThrottle()
            elif inp == '\x1b[B':
                print("Down\r\n")
                self.drone.decreaseThrottle()
            elif inp == '\x1b[C':
                print("Right\r\n")
                self.drone.increaseYaw()
            elif inp == '\x1b[D':
                print("Left\r\n")
                self.drone.decreaseYaw()

            elif inp == 'w':
                print("w\r\n")
                self.drone.decreasePitch()
            elif inp == 's':
                self.drone.increasePitch()
            elif inp == 'a':
                self.drone.increaseRoll()
            elif inp == 'd':
                self.drone.decreaseRoll()
            
            elif inp == '\x1b\x1b':
                print("Esc")
                
                self.drone.exitMe()
                self.stopConsole()

            elif inp == 'g':
                self.drone.startControlManual() 
            elif inp == 'h':
                self.drone.stopControlManual() 
            elif inp == ' ':
                self.drone.arm() 
            elif inp == '1':
                self.drone.stabilize()
            elif inp == '2':
                self.drone.loiter()
            elif inp == '3':
                self.drone.posHold()
            elif inp == '4':
                self.drone.altHold()
            elif inp == '0':
                self.drone.land() 
            elif inp == '9':
                self.drone.rtl()
            elif inp == 'l' and self.doCapture is not None:
                self.doCapture()
            elif inp == 'k' and self.dontCapture is not None:
                self.dontCapture()    
            elif inp == 'm':
                self.drone.calibrateGyro()
            elif inp == 'n':
                self.drone.calibrateLevel()
            elif inp == 'b':
                self.drone.killMe()
            elif inp == ',':
                self.drone.calibratePressure()
            elif inp == 'z':
                self.drone.goForward()

            else:
                print(repr(inp))
            

if __name__ == '__main__':
    mc = MyConsole()    
    mc.startConsole()
    while(mc.started):
        sleep(0.5)    

        

