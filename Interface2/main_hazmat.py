from os.path import join
from detector import Yolov3


class HAZMAT():
    def __init__(self):
        #parameters
        self.k = 0
        self.net_directory = 'net'
        self.min_confidence=0.8
        self.nms_threshold=0.3
        self.segmentation_enabled=True

        self._detector = Yolov3 (
            weights=join(self.net_directory, 'yolo.weights'),
            config=join(self.net_directory, 'yolo.cfg'),
            labels=join(self.net_directory, 'labels.names'),
            input_size=(576, 576),
            min_confidence=self.min_confidence,
            nms_threshold=self.nms_threshold,
            segmentation_enabled=self.segmentation_enabled,
        )

        #optimisation
        self.q = 2 ** self.k
        self.p = self.q
        self.n = 0
        self.last_objetcs = []

    def update(self, frame):
        self.n += 1
        if self.n < self.p:
            return self.last_objects

        self.n = 0
        self.last_objects = self._detector.detect(frame)
        if len(self.last_objects) > 0:
            if self.p > 1:
                self.p //= 2
        else:
            if self.p < self.q:
                self.p *= 2
        return self.last_objects

    def draw(self, image):
        for hazmat in self.update(image):
            hazmat.draw(image=image, padding=0.1)
        return image

