import cv2


class VideoProcessor:
    def __init__(self, video_path: str):
        """
        Initializes the video capture.

        Args:
            video_path (str): Path to the video file.
        """
        self.cap = cv2.VideoCapture(video_path)

    def get_frame(self):
        """
        Reads the next frame from the video.

        Returns:
            np.ndarray or None: The video frame if available, else None.
        """
        ret, frame = self.cap.read()
        # If the frame is not available, return None
        if not ret:

            return None
        return frame

    def release(self):
        """Releases the video capture resource."""
        self.cap.release()
