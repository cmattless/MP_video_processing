import cv2
import os

from src.core.video_utils.video_queue import VideoQueue

class ArchiveProcessor:
    """
    ArchiveProcessor handles the creation of a video file by writing
    processed frames to a specified output location.
    """
    def __init__(self, output_path: str, fps: int = 30, frame_size: tuple = (640, 480)):
        """
        Initializes the video writer and ensures the output directory exists.
        :param output_path: Path where the output video will be saved.
        :param fps: Frames per second for the output video.
        :param frame_size: Tuple indicating (width, height) of the video frames.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size, True)

        if not self.video_writer.isOpened():
            raise IOError(f"Cannot open {output_path} for writing.")

    def write_frame(self, frames: VideoQueue) -> None:
        """
        Writes a single processed frame to the video file.
        :param frame: The processed frame (must match the frame_size and color format).
        """

        for i in range(frames.size()):
            self.video_writer.write(frames.dequeue())

    def release(self) -> None:
        """
        Releases the video writer resource. Must be called after all frames are written.
        """
        self.video_writer.release()
