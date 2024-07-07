
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
        from deep_hazmat import visualizer
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
