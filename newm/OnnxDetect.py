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
        weights = glob.glob("/home/jetson/yolo/onnx/best7n.onnx")[0]
        labels = glob.glob("/home/jetson/yolo/yolov4/coco.names")[0]
        # cfg = glob.glob("/home/jetson/yolo/yolov4/yolov4-tiny.cfg")[0]
        self.lbls = list()
        with open(labels, "r") as f:
            self.lbls = [c.strip() for c in f.readlines()]
        self.COLORS = np.random.randint(0, 255, size=(len(self.lbls), 3), dtype="uint8")
        self.net = cv2.dnn.readNet(weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
 
        self.goPitch = False
        self.INPUT_WIDTH = 640
        self.INPUT_HEIGHT = 640
        self.SCORE_THRESHOLD = 0.2
        self.NMS_THRESHOLD = 0.4
        self.CONFIDENCE_THRESHOLD = 0.4

    def detector(self,image):
        blob = cv2.dnn.blobFromImage(image, 1/255.0, (self.INPUT_WIDTH, self.INPUT_HEIGHT), swapRB=True, crop=False)
        self.net.setInput(blob)
        preds = self.net.forward()
        return preds


    def wrap_detection(self,input_image, output_data):
        class_ids = []
        confidences = []
        boxes = []

        rows = output_data.shape[0]

        image_width, image_height, _ = input_image.shape

        x_factor = image_width / self.INPUT_WIDTH
        y_factor =  image_height / self.INPUT_HEIGHT

        for r in range(rows):
            row = output_data[r]
            confidence = row[4]
            if confidence >= 0.4:

                classes_scores = row[5:]
                _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
                class_id = max_indx[1]
                if (classes_scores[class_id] > .25):

                    confidences.append(confidence)

                    class_ids.append(class_id)

                    x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
                    left = int((x - 0.5 * w) * x_factor)
                    top = int((y - 0.5 * h) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)
                    box = np.array([left, top, width, height])
                    boxes.append(box)

        result_class_ids = []
        result_confidences = []
        result_boxes = []

        if len(boxes) > 0 and len(confidences) > 0:
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45)  
            for i in indexes:
                result_confidences.append(confidences[i])
                result_class_ids.append(class_ids[i])
                result_boxes.append(boxes[i])

        return result_class_ids, result_confidences, result_boxes

    def detect(self,image):  
        (H, W) = image.shape[:2]
        self.pid.setpoint = int(W / 2)
        
        


        frame = image
        t0 = time.time()
        inputImage = self.format_yolov5(frame)
        t1 = time.time()
        # print(f"formatYolov5: {(t1-t0)}")
        outs = self.detector(inputImage)
        # print(f"detection: {(time.time()-t1)}")
        class_ids, confidences, boxes = self.wrap_detection(inputImage, outs[0])


        colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (255, 0, 0)]

        for (classid, confidence, box) in zip(class_ids, confidences, boxes):
            color = colors[int(classid) % len(colors)]
            cv2.rectangle(frame, box, color, 2)
            cv2.rectangle(frame, (box[0], box[1] - 20), (box[0] + box[2], box[1]), color, -1)
            cv2.putText(frame, self.lbls[classid], (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0))

        return frame
        # boxes = list()
        # confidences = list()
        # class_ids = list()

        # for output in layer_outs:
        #     for detection in output:
        #         scores = detection[5:]
        #         class_id = np.argmax(scores)
        #         confidence = scores[class_id]

        #         if confidence > self.CONFIDENCE_THRESHOLD:
        #             box = detection[0:4] * np.array([W, H, W, H])
        #             (center_x, center_y, width, height) = box.astype("int")

        #             x = int(center_x - (width / 2))
        #             y = int(center_y - (height / 2))

        #             boxes.append([x, y, int(width), int(height)])
        #             confidences.append(float(confidence))
        #             class_ids.append(class_id)

        # idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)
        # # print(f"Len: {len(idxs)}")
        # centerX = -1
        # targetArea = -1
        # if len(idxs) > 0:
        #     for i in idxs.flatten():
        #         (x, y) = (boxes[i][0], boxes[i][1])
        #         (w, h) = (boxes[i][2], boxes[i][3])

        #         color = [int(c) for c in self.COLORS[class_ids[i]]]
                
        #         text = "{}: {:.4f}".format(self.lbls[class_ids[i]], confidences[i])
        #         if(f"{self.lbls[class_ids[i]]}" == "person"):
        #             centerX = x + int(w /2)
        #             cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        #             cv2.putText(
        #                 image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
        #             )
        #             targetArea = w*h
        #             print(f"Prop: {(targetArea)/(H*W)}\r\n")
        #         else:
        #             cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        #             cv2.putText(
        #                 image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
        #             )
        #         label = "Inference Time: {:.2f} s ".format(end_time - start_time)
        #         label = f"{label} W:{W} H:{H}"
        #         cv2.putText(
        #             image, label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
        #         )
        # baseCenterX = int(W / 2)
        




        # if(centerX != -1): 
        #     threading.Thread(target=self.controlDeviceYaw,args=(baseCenterX,centerX)).start()
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
        print(f"=== output: {out}\r\n")
        absout = abs(out)
        num = 1
        if(absout > 300):
            num= 5
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
            print("stop yaw\r\n")
            self.quad.yaw = 1500
        elif(out > 0):
            print("Go Left\r\n")
            self.quad.yaw = 1500
            self.quad.decreaseYaw(num)
        else:
            print("go Right\r\n")
            self.quad.yaw = 1500
            self.quad.increaseYaw(num)

    def format_yolov5(self,frame):
        row, col, _ = frame.shape
        _max = max(col, row)
        result = np.zeros((_max, _max, 3), np.uint8)
        result[0:row, 0:col] = frame
        return result


