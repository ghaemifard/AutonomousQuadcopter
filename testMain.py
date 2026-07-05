import sys,tty,termios
from time import sleep, time
from MyVehicle import MyQuad
import numpy as np
import cv2
quad = None
class _Getch:
    def __call__(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(3)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch




def get(quad:MyQuad):
        inkey = _Getch()
        while(1):
                k=inkey()
                if k!='':break
        if k=='\x1b[A':
                print ("up")
                quad.increaseThrottle()
        elif k=='\x1b[B':
                print ("down")
                quad.decreaseThrottle()
        elif k=='\x1b[C':
                print ("right")
                quad.increaseYaw()
        elif k=='\x1b[D':
                print ("left")
                quad.decreaseYaw()
        elif k=='ttt':
            print("T")
        else:
                print ("not an arrow key!")
        return k

def main():

        t0 = time()
        sleep(.2)
        print(f"elapsed: {time()-t0}")
        if(True):
                return
        quad = MyQuad("/dev/ttyACM0")
        # quad.printParams()
        quad.setParameter("RC_OVERRIDE_TIME",30)
        pa = quad.getParameter("RC_OVERRIDE_TIME")
        print(f"param: {pa}")
        quad.setStablizeMode()
        quad.arm()
        quad.setDefaultThrottle()
        quad.setDefaultYaw()
       
        str = get(quad)
        while (str != 'qqq'):
                str = get(quad)
        # while(str != "qqq" and str != ''):
        #         inkey = _Getch()
        #         while(1):
        #                 str = inkey()
        #                 if str =='': break
        #         if str=='\x1b[A':
        #                 print("UP")
        #                 quad.increaseThrottle()
        #         elif str == '\x1b[B':
        #                 print("down")
        #                 quad.decreaseThrottle()


        quad.disarm()
        quad.closeDrone()

if __name__=='__main__':
        
        # t0 = time()
        # sleep(.3)
        # print(f"{time()-t0}")

        green = np.uint8([[[57,55,42 ]]])
        hsv_green = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
        print( hsv_green )
        # main()