import cv2
from core.video_utils.video_queue import VideoQueue


# This class takes frames from the video_queue and writes them to a video file. This class is a singleton.

class ArchiveProcessor:
    def __init__(self, output_path: str, fps: int, frame_size: tuple):
        """
        Initializes the ArchiveProcessor class.
        """

        if hasattr (ArchiveProcessor, "instance"):
            raise Exception("This class is a singleton!")
        

        self.output_path = output_path
        self.fps = fps
        self.frame_size = frame_size
        self.out = cv2.VideoWriter(self.output_path, cv2.VideoWriter_fourcc(*"XVID"), self.fps, self.frame_size)
        self.instance = True

    def write_frame(self, frame: VideoQueue) -> None:
        """
        Writes a frame to the video file.

        Args:
            frame (np.ndarray): The frame to write.
        """
        self.out.write(frame)
