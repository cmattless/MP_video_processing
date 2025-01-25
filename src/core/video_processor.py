import cv2

class VideoProcessor:
    def __init__(self, video_path: str):
        self.cap = cv2.VideoCapture(video_path)

    def get_frame(self):
        """Retrieve the next frame from the video."""
        ret, frame = self.cap.read()
        if not ret:
            return None  # No more frames
        return frame

    def release(self):
        """Release video resources."""
        self.cap.release()
