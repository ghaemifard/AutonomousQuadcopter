import time
class MyStatics:
    loop = None
    goPitch = False
    myM = False
    recording = False
    def makePitchForseconds(self,n):
        if not MyStatics.goPitch:
            MyStatics.goPitch = True
            time.sleep(n)
            MyStatics.goPitch = False