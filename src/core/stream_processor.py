import cv2

class StreamProcessor:
    def __init__(self, stream_source: int = 0):
        self.cap = cv2.VideoCapture(stream_source)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()
