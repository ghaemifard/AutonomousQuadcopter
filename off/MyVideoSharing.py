       
from unittest import runner
import cv2
import time
import threading
from flask import Response, Flask
from YoloDetection import Detection
from MavVehicle import MyQuad
import asyncio
from CharUtil import *

# Image frame sent to the Flask object
global video_frame
video_frame = None


# Use locks for thread-safe viewing of frames in multiple browsers
global thread_lock 
thread_lock = threading.Lock()

# GStreamer Pipeline to access the Raspberry Pi camera
GSTREAMER_PIPELINE = 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=21/1 ! nvvidconv flip-method=0 ! video/x-raw, width=960, height=616, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink wait-on-eos=false max-buffers=1 drop=True'

# Create the Flask object for the application
app = Flask(__name__)
global number
global rruunn
async def startLooping():
    global rruunn
    rruunn = True

    while rruunn:
        await asyncio.sleep(.05)

    print("event loop finished")


def captureFrames(loop):
    global video_frame, thread_lock, number, rruunn
    number = 0
    
    asyncio.set_event_loop(MyStatics.loop)
 
    print("before init")
    quad = MyQuad()
    asyncio.ensure_future(quad.init())
    time.sleep(5)

    asyncio.ensure_future(quad.arm())
    time.sleep(1)

    asyncio.ensure_future(quad.startManualControl())
    time.sleep(.3)
    
    quad.changeThrottle(.7)
    time.sleep(3)
    quad.changeThrottle(.4)
    time.sleep(2)
    quad.changeThrottle(.3)

    detection = Detection(quad)

    
    # Video capturing from OpenCV
    video_capture = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)



    while True and video_capture.isOpened():
        return_key, frame = video_capture.read()
        if not return_key:
            break

        # Create a copy of the frame and store it in the global variable,
        # with thread safe access
        number = number + 1
        if(number % 2 == 0):
            frame = detection.detect(frame)
            with thread_lock:
                video_frame = frame.copy()
        
        
        if number > 400:
            break
    
    quad.yaw = 0
    quad.stopManualControl()
    video_capture.release()
    asyncio.ensure_future(quad.disarm())
    time.sleep(2)
    asyncio.ensure_future(quad.close())
    rruunn = False

def captureFrames(loop):
    global video_frame, thread_lock, number, rruunn
    number = 0
    
    asyncio.set_event_loop(MyStatics.loop)
 
    print("before init")
    quad = MyQuad()
    asyncio.ensure_future(quad.init())
    time.sleep(5)

    asyncio.ensure_future(quad.arm())
    time.sleep(1)

    asyncio.ensure_future(quad.startManualControl())
    time.sleep(.3)
    
    quad.changeThrottle(.7)
    time.sleep(3)
    quad.changeThrottle(.4)
    time.sleep(2)
    quad.changeThrottle(.3)

    detection = Detection(quad)

    
    # Video capturing from OpenCV
    video_capture = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)



    while True and video_capture.isOpened():
        return_key, frame = video_capture.read()
        if not return_key:
            break

        # Create a copy of the frame and store it in the global variable,
        # with thread safe access
        number = number + 1
        if(number % 2 == 0):
            frame = detection.detect(frame)
            with thread_lock:
                video_frame = frame.copy()
        
        
        if number > 400:
            break
    
    quad.yaw = 0
    quad.stopManualControl()
    video_capture.release()
    asyncio.ensure_future(quad.disarm())
    time.sleep(2)
    asyncio.ensure_future(quad.close())
    rruunn = False

        
def encodeFrame():
    global thread_lock
    while True:
        # Acquire thread_lock to access the global video_frame object
        with thread_lock:
            global video_frame
            if video_frame is None:
                continue
            return_key, encoded_image = cv2.imencode(".jpg", video_frame)
            if not return_key:
                continue

        # Output image as a byte array
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encoded_image) + b'\r\n')

@app.route("/")
def streamFrames():
    return Response(encodeFrame(), mimetype = "multipart/x-mixed-replace; boundary=frame")

# # check to see if this is the main thread of execution
# if __name__ == '__main__':

#     loop = asyncio.get_event_loop()
#     MyStatics.loop = loop
#     # Create a thread and attach the method that captures the image frames, to it
#     process_thread = threading.Thread(target=captureFrames,args=(loop,))
#     process_thread.daemon = True

#     # Start the thread
#     process_thread.start()

    
#     threading.Thread(target=lambda:loop.run_until_complete(startLooping())).start()
#     # start the Flask Web Application
#     # While it can be run on any feasible IP, IP = 0.0.0.0 renders the web app on
#     # the host machine's localhost and is discoverable by other machines on the same network 
#     app.run("0.0.0.0", port="8008")
# check to see if this is the main thread of execution
def myMain():

    loop = asyncio.get_event_loop()
    MyStatics.loop = loop
    # Create a thread and attach the method that captures the image frames, to it
    process_thread = threading.Thread(target=captureFrames,args=(loop,))
    process_thread.daemon = True

    # Start the thread
    process_thread.start()

    
    threading.Thread(target=lambda:loop.run_until_complete(startLooping())).start()
    # start the Flask Web Application
    # While it can be run on any feasible IP, IP = 0.0.0.0 renders the web app on
    # the host machine's localhost and is discoverable by other machines on the same network 
    app.run("0.0.0.0", port="8008")

