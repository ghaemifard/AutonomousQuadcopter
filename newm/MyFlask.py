       
import cv2
import time
import threading
from flask import Response, Flask 
from InputReader import MyConsole
from MyDrone import Drone
from Detect import Detection
from MySock import MySocket
# Image frame sent to the Flask object
global video_frame
video_frame = None

global doCap
doCap = True

# Use locks for thread-safe viewing of frames in multiple browsers
global thread_lock 
thread_lock = threading.Lock()

# GStreamer Pipeline to access the Raspberry Pi camera
GSTREAMER_PIPELINE = 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=21/1 ! nvvidconv flip-method=0 ! video/x-raw, width=960, height=616, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink wait-on-eos=false max-buffers=1 drop=True'
# GSTREAMER_PIPELINE = 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=21/1 ! nvvidconv ! video/x-raw, width=640, height=640, format=(string)BGRx  ! videoconvert ! video/x-raw ! appsink wait-on-eos=false max-buffers=1 drop=True'

# Create the Flask object for the application
app = Flask(__name__)
global number
def captureFrames():
    global video_frame, thread_lock, number, doCap
    number = 0
    # Video capturing from OpenCV
    video_capture = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
    det = Detection()
    drone = Drone.getInstance()

    while  video_capture.isOpened() and doCap:
        return_key, frame = video_capture.read()
        if not return_key:
            break

        # Create a copy of the frame and store it in the global variable,
        # with thread safe access
        number = number + 1
        if(number % 2 == 0): 
            with thread_lock:
                # video_frame  = det.detect(cv2.cvtColor(frame.copy(),cv2.COLOR_RGB2BGR))
                tt = time.time()
                # video_frame  = det.detect2(cv2.rotate(frame.copy(),cv2.ROTATE_90_COUNTERCLOCKWISE))

                if drone.rc_override:
                    video_frame  = det.detect2(frame.copy())
                else:
                    video_frame  = frame.copy()


                # fr = frame.copy()
                
                # video_frame  = fr
                 
                # print(f"rotation time: {time.time()-tt} \r\n")

        # if number > 800:
        #     break
    
    video_capture.release() 
    
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

def startCapture(): 
    global doCap
    doCap = True
    # Create a thread and attach the method that captures the image frames, to it
    process_thread = threading.Thread(target=captureFrames) 
    process_thread.daemon = True  
    process_thread.start()

def stopCaptue():
    global doCap
    doCap = False
# check to see if this is the main thread of execution
if __name__ == '__main__':
    socket = MySocket.getInstance()
    mc = MyConsole.getInstance()
    mc.doCapture = startCapture
    mc.dontCapture = stopCaptue

    socket.doCapture = startCapture
    socket.dontCapture = stopCaptue
    mc.startConsole()

   

    # start the Flask Web Application
    # While it can be run on any feasible IP, IP = 0.0.0.0 renders the web app on
    # the host machine's localhost and is discoverable by other machines on the same network 
    app.run("0.0.0.0", port="8008")

