from ast import arg
from cgitb import reset
from posixpath import abspath
import cv2
import numpy as np
import glob
import time 
from simple_pid import PID
from MavVehicle import *
from MyStatistics import MyStatics

class Detection:
    def __init__(self,quad:MyQuad) -> None:
        self.pid = PID(.95, 0, .02)
        self.quad = quad
        self.CONFIDENCE_THRESHOLD = .5
        self.NMS_THRESHOLD = .4
        weights = glob.glob("/home/jetson/yolo/yolov4/yolov4-tiny.weights")[0]
        labels = glob.glob("/home/jetson/yolo/yolov4/coco.names")[0]
        cfg = glob.glob("/home/jetson/yolo/yolov4/yolov4-tiny.cfg")[0]
        self.lbls = list()
        with open(labels, "r") as f:
            self.lbls = [c.strip() for c in f.readlines()]
        self.COLORS = np.random.randint(0, 255, size=(len(self.lbls), 3), dtype="uint8")
        self.net = cv2.dnn.readNetFromDarknet(cfg, weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        self.layer = self.net.getLayerNames()
        self.layer = [self.layer[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        self.goPitch = False

    def testColor(self,image):
        (H, W) = image.shape[:2]
        self.pid.setpoint = int(W / 2)
        image = cv2.GaussianBlur(image,(5,5),0)
        # Convert BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv,(11,11),0)
        # define blue color range
        # t0 = time.time()
        # light_blue = np.array([110,50,50])
        # dark_blue = np.array([130,190,190])

        # t0 = time.time()
        # light_blue = np.array([85,140,140]) very good
        # dark_blue = np.array([115,250,250]) very good

        t0 = time.time()
        light_blue = np.array([85,100,100])
        dark_blue = np.array([115,250,250])


        # lower bound and upper bound for Green color
        lower_bound = np.array([50, 20, 20])   
        upper_bound = np.array([100, 255, 255])

        lower_black = np.array([0, 0, 0])
        upper_black = np.array([350,55,100])

        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, light_blue, dark_blue)

        # kernel = np.ones((5,5))
        # mask =   cv2.dilate(mask, kernel)
        # Bitwise-AND mask and original image
        # mask = cv2.erode(mask,None,iterations=2)
        # mask = cv2.dilate(mask,None,iterations=2)



        # contours
        contours,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        center = None
        imgOriginal = image
        targetArea = None
        rect = None
        if len(contours) > 0:

            # get max contour
            c = max(contours, key=cv2.contourArea)

            # return rectangle
            rect = cv2.minAreaRect(c)
            ((x,y), (width, height), rotation) = rect

            s = f"x {np.round(x)}, y: {np.round(y)}, width: {np.round(width)}, height: {np.round(height)}, rotation: {np.round(rotation)}\r\n"
            print(s)
            targetArea = np.round(width) * np.round(height)
            # box
            box = cv2.boxPoints(rect)
            box = np.int64(box)

            # moment
            M = cv2.moments(c)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # draw contour
            cv2.drawContours(imgOriginal, [box], 0, (0, 255, 255), 2)

            # point in center
            cv2.circle(imgOriginal, center, 5, (255, 0, 255), -1)

            # print inform
            cv2.putText(imgOriginal, s, (25, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2)


        # deque
        # pts.appendleft(center)
        # for i in range(1, len(pts)):

        #     if pts[i - 1] is None or pts[i] is None: continue

        #     cv2.line(imgOriginal, pts[i - 1], pts[i], (0, 255, 0), 3)

        output = cv2.bitwise_and(image,image, mask= mask)

        
        res = np.hstack((image,output))

        baseCenterX = int(W / 2)
        MyStatics.recording = True
        baseCenterX = int(W / 2)
        MyStatics.recording = True
        if(center is not None and targetArea > 100):
            self.controlDevicePitch(targetArea,W*H)
            threading.Thread(target=self.controlDeviceYaw,args=(baseCenterX,center[0])).start()
            # if(abs(centerX-baseCenterX) < 50):
            #     print("stop moving")
            #     self.quad.setDefaultYaw()
            # elif(centerX-baseCenterX>0):
            #     print("Go Right")
            #     self.quad.setDefaultYaw()
            #     self.quad.increaseYaw()
            # else:
            #     print("Go left")
            #     self.quad.setDefaultYaw()
            #     self.quad.decreaseYaw()

        return res
    def detect(self,image): 
        if(True):
            return self.testColor(image)
        (H, W) = image.shape[:2]
        self.pid.setpoint = int(W / 2)
        # print(f"{W}x{H}")
        blob = cv2.dnn.blobFromImage(image, 1 / 255, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        start_time = time.time()
        layer_outs = self.net.forward(self.layer)
        end_time = time.time()
        # print(f"elapsed time is {end_time - start_time}")

        boxes = list()
        confidences = list()
        class_ids = list()

        for output in layer_outs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > self.CONFIDENCE_THRESHOLD:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (center_x, center_y, width, height) = box.astype("int")

                    x = int(center_x - (width / 2))
                    y = int(center_y - (height / 2))

                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)
        # print(f"Len: {len(idxs)}")
        centerX = -1
        targetArea = -1
        if len(idxs) > 0:
            for i in idxs.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                color = [int(c) for c in self.COLORS[class_ids[i]]]
                
                text = "{}: {:.4f}".format(self.lbls[class_ids[i]], confidences[i])
                if(f"{self.lbls[class_ids[i]]}" == "person"):
                    centerX = x + int(w /2)
                    cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(
                        image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                    )
                    targetArea = w*h
                    print(f"Prop: {(targetArea)/(H*W)}\r\n")
                else:
                    cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(
                        image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                    )
                label = "Inference Time: {:.2f} s".format(end_time - start_time)
                cv2.putText(
                    image, label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
                )
        baseCenterX = int(W / 2)
        MyStatics.recording = True
        if(centerX != -1):
            self.controlDevicePitch(targetArea,W*H)
            threading.Thread(target=self.controlDeviceYaw,args=(baseCenterX,centerX)).start()
            # if(abs(centerX-baseCenterX) < 50):
            #     print("stop moving")
            #     self.quad.setDefaultYaw()
            # elif(centerX-baseCenterX>0):
            #     print("Go Right")
            #     self.quad.setDefaultYaw()
            #     self.quad.increaseYaw()
            # else:
            #     print("Go left")
            #     self.quad.setDefaultYaw()
            #     self.quad.decreaseYaw()
        return image

    def controlDevicePitch(self,targetArea:float,area:float):
        asyncio.set_event_loop(MyStatics.loop)
        rightApprop = .7
        if(MyStatics.goPitch):
            if(targetArea/area<rightApprop):
                self.quad.goForward()
            else:
                self.quad.stopPitch()
        else:
            self.quad.stopPitch()
            

    def controlDeviceYaw(self,baseCenterX,centerX):
        asyncio.set_event_loop(MyStatics.loop)
        if(abs(baseCenterX-centerX)<30):
            centerX = baseCenterX
        out = self.pid(centerX)
        print(f"=== output: {out}")
        absout = abs(out)
        num = 1
        if(absout > 300):
            num = 5
        elif (absout>250):
            num = 5
        elif (absout>200):
            num = 2
        elif (absout>150):
            num = 2
        elif (absout>100):
            num = 1
        elif (absout>50):
            num = 1
        
        
        if(absout < 30):
            print("stop yaw")
            # self.quad.yaw = float(0.0)
        elif(out > 0):
            print("Go Left")
            # self.quad.yaw = float(0.0)

            self.quad.leftYaw(num)
        else:
            print("go Right")
            # self.quad.yaw = float(0.0)
            self.quad.rightYaw(num)
