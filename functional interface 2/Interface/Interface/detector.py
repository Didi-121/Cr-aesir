import cv2
import time
import numpy as np

from segmentation import Segmentation
import nms
import visualizer


color_list = [
    (220, 120, 50),  # poison
    (160, 30, 10),  # oxygen
    (50, 220, 220),  # flammable gas
    (120, 120, 50),  # flammable-solid
    (20, 120, 50),  # corrosive
    (50, 180, 150),  #dangerous when wet
    (40, 40, 160),  # non-flammable-gas
    (210, 80, 30),  # organic-peroxide
    (120, 120, 180),  # explosive
    (255, 130, 130),  # radioactive
    (80, 170, 100),  # inhalation-hazard
    (80, 200, 20),  # spontaneously-combustible
    (120, 120, 140),  # infectious-substance
    (120, 120, 180), #blasting agents
    (50, 220, 220), #fuel oil
    (160, 30, 10),  # oxidizer
]
class Yolov3:
    def __init__(self, weights, config, labels, input_size=(416, 416),
                 min_confidence=0.7, nms_threshold=0.3, segmentation_enabled=True):

        self._net = cv2.dnn.readNetFromDarknet(config, weights)
        self._labels = open(labels).read().strip().split("\n")
        self._colors = color_list[:len(self._labels)]

        self._layer_names = self._net.getLayerNames()
        self._layer_names = [self._layer_names[i - 1]
                             for i in self._net.getUnconnectedOutLayers()]
        self.min_confidence = min_confidence
        self.nms_threshold = nms_threshold

        self.input_size = input_size
        self.segmentation_enabled = segmentation_enabled

    def detect(self, image):
        blob = cv2.dnn.blobFromImage(
            image,
            1 / 255.0,
            self.input_size,
            swapRB=True,
            crop=False
        )
        self._net.setInput(blob)
        H, W = image.shape[:2]

        boxes = []
        for output in self._net.forward(self._layer_names):
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.min_confidence:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, x + int(width), y + int(height), confidence, class_id])

        if not boxes:
            return []

        class_ids = []
        positions = []
        confidences = []
        for box in boxes:
            p = box[:4]
            p[2] -= p[0]
            p[3] -= p[1]
            positions.append(p)
            confidences.append(float(box[4]))
            class_ids.append(box[5])

        if self.nms_threshold > 0:
            boxes = nms.non_max_suppression(boxes, self.nms_threshold)

        objects = []
        for box in boxes:
            x, y, x2, y2 = [int(i) for i in box[:4]]
            w = x2 - x
            h = y2 - y
            x /= W
            w /= W
            h /= H
            y /= H
            confidence = box[4]
            class_id = int(box[5])
            if self.segmentation_enabled:
                segmentation = Segmentation(image, [x, y, w, h])
                points = segmentation.find_object(padding=0.1)
            else:
                points = []
            objects.append(Object(
                x, y, w, h,
                confidence=confidence,
                name=self._labels[class_id],
                color=[int(c) for c in self._colors[class_id]],
                points=points,
            ))

        return objects

class Object:
    def __init__(self, x, y, w, h, confidence, name, color, points):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.confidence = confidence
        self.name = name
        self.color = color
        self.points = points

    def draw(self, image, padding=0.1):
        h, w = image.shape[:2]
        visualizer.draw_lines(image, self.points)
        visualizer.draw_box(
            image,
            int(self.x * w),
            int(self.y * h),
            int(self.w * w),
            int(self.h * h),
            self.color,
            '{}:{}%'.format(self.name, int(self.confidence * 100)),
            padding=padding,
        )