import cv2
from video_utils.video_queue import VideoQueue

class StreamProcessor:

    def __init__(self, stream_source: int = 0):
        """
        Initializes the stream capture.

        args:
            stream_source (int): Source
        """
        self.cap = cv2.VideoCapture(stream_source)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def get_frame(self):
        """
        Reads the next frame from the stream.

        Returns:
            np.ndarray or None: The video frame if available, else None.
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        VideoQueue.enqueue(frame)
        return frame

    def release(self):
        """
        Releases the stream capture resource
        """
        self.cap.release()
