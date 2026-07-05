from ast import arg
from cgitb import reset
from posixpath import abspath
import cv2
import numpy as np
import glob
import time 
from simple_pid import PID 
from MyDrone import Drone
import threading
class Detection:
    def __init__(self) -> None:
        self.pid = PID(.95, 0, .02)
        self.quad = Drone.getInstance()
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

    def detect(self,image):  
        (H, W) = image.shape[:2]
        self.pid.setpoint = int(W / 2)
        # print(f"{W}x{H}")
        start_time = time.time()
        blob = cv2.dnn.blobFromImage(image, 1 / 255, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        end_time = time.time()
        print(f"inference elapsed time is {end_time - start_time} \r\n")
        
        layer_outs = self.net.forward(self.layer)

        boxes = list()
        confidences = list()
        class_ids = list()
        for output in layer_outs:
            # print("---------------\r\n")
            for detection in output:
                scores = detection[5:]
                # print(f"{detection}\r\n")
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
                label = "Inference Time: {:.2f} s ".format(end_time - start_time)
                label = f"{label} W:{W} H:{H}"
                cv2.putText(
                    image, label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
                )
        baseCenterX = int(W / 2)
        
        if(centerX != -1): 
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
        # return image

        
    def detect2(self,image):  
        (H, W) = image.shape[:2]
        self.pid.setpoint = int(W / 2)
        # print(f"{W}x{H}")
        start_time = time.time()
        blob = cv2.dnn.blobFromImage(image, 1 / 255, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)

        layer_outs = self.net.forward(self.layer)

        end_time = time.time()
        boxes = list()
        confidences = list()
        class_ids = list()
        # start_time = time.time()
        for output in layer_outs:
            # print(f"len out: {len(output)}---------------\r\n")
            # start_time = time.time()
            for detection in output:
                scores = detection[5:6]
                # if len(output>1000):
                #     print(f"{len(detection)}\r\n")

                # class_id = np.argmax(scores)
                # confidence = scores[class_id]
                
                class_id = 0
                confidence = scores[class_id]

                if confidence > self.CONFIDENCE_THRESHOLD:
                    # box = detection[0:4] * np.array([W, H, W, H])
                    # (center_x, center_y, width, height) = box.astype("int")


                    center_x   = int(detection[0] * W)
                    center_y   = int(detection[1] * H)
                    width = int(detection[2] * W)
                    height = int(detection[3] * H)
                    
                    x = int(center_x - (width / 2))
                    y = int(center_y - (height / 2))

                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)
        
        
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
                label = "Inference Time: {:.2f} s ".format(end_time - start_time)
                label = f"{label} W:{W} H:{H}"
                cv2.putText(
                    image, label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
                )
        baseCenterX = int(W / 2)
        
        if(centerX != -1): 
            threading.Thread(target=self.controlDeviceYaw,args=(baseCenterX,centerX)).start()
            threading.Thread(target=self.controlPitch,args=(targetArea,W*H)).start()
        else:
            self.nullify()

        return image

    def nullify(self):
        self.quad.pitch = 1500
        self.quad.yaw = 1500
    def controlPitch(self,targetArea:float,area:float):
        if self.quad.goJelou:
            prop = targetArea/area
            if (prop<.7):
                self.quad.printSocket("Go Forward")
                self.quad.decreasePitch()
            elif (prop>.9):
                self.quad.printSocket("Go Backward")
                self.quad.increasePitch()
            else:
                self.quad.printSocket("Stop Pitch")
                self.quad.pitch = 1500
        else:
            self.quad.pitch = 1500
    def controlDevicePitch(self,targetArea:float,area:float):
        # asyncio.set_event_loop(MyStatics.loop)
        rightApprop = .7
        # if(MyStatics.goPitch):
        #     if(targetArea/area<rightApprop):
        #         self.quad.goForward()
        #     else:
        #         self.quad.stopPitch()
        # else:
        #     self.quad.stopPitch()
            

    def controlDeviceYaw(self,baseCenterX,centerX): 
        if(abs(baseCenterX-centerX)<30):
            centerX = baseCenterX
        out = self.pid(centerX)
        print(f"output: {out}\r\n")
        absout = abs(out)
        num = 1
        if(absout > 300):
            num= 5
        elif (absout>250):
            num = 4
        elif (absout>200):
            num = 3
        elif (absout>150):
            num = 2
        elif (absout>100):
            num = 1
        elif (absout>50):
            num = 1
        
        
        if(absout < 30):
            self.quad.printSocket("stop yaw")
            self.quad.yaw = 1500
        elif(out > 0):
            self.quad.printSocket("Go Left")
            self.quad.yaw = 1500
            self.quad.decreaseYaw(num)
        else:
            self.quad.printSocket("go Right")
            self.quad.yaw = 1500
            self.quad.increaseYaw(num)