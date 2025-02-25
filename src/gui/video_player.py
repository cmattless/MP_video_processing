import cv2
import queue
import threading
import multiprocessing as mp
from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

from core.video_processor import VideoProcessor
from core.stream_processor import (
    StreamProcessor,
)  # New import for live stream processing
from core.model_processor import Model


def draw_object_contours(img, tracked_objects):
    """
    For each detected object (with a bounding box), extract the region,
    run edge detection to obtain object contours, and draw them on the image.
    If no clear contour is found, fall back to drawing the bounding box.

    Args:
        img (np.ndarray): The image on which to draw.
        tracked_objects (list): List of detected objects.
            Each detection must include:
                - "bbox": [x, y, w, h] bounding box.
                - "track_id": an identifier.

    Returns:
        np.ndarray: Image with drawn contours (or bounding boxes as fallback).
    """
    for track in tracked_objects:
        x, y, w, h = map(int, track["bbox"])
        roi = img[y : y + h, x : x + w]
        if roi.size == 0:
            continue

        # gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # edges = cv2.Canny(blurred, 50, 150)
        # contours, _ = cv2.findContours(
        #     edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        # )

        # if contours:
        #     largest_contour = max(contours, key=cv2.contourArea)
        #     largest_contour += [x, y]
        #     cv2.drawContours(img, [largest_contour], -1, (0, 255, 0), 1)
        #     label = f"ID {track['track_id']}"
        #     cv2.putText(
        #         img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
        #     )
        # else:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        label = f"ID {track['track_id']}"
        cv2.putText(
            img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
        )
    return img


def process_frames_worker(frame_queue, processed_queue, model_path):
    """
    Process frames in a separate process.

    Initializes the model and continuously pulls frames from frame_queue,
    processes them, draws object contours (or bounding boxes as fallback),
    and pushes the processed frame to processed_queue.
    """
    model = Model(model_path)
    while True:
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        tracked_objects = model.process_frame(frame)
        processed_frame = draw_object_contours(frame, tracked_objects)
        processed_queue.put(processed_frame)


class VideoPlayer(QMainWindow):
    def __init__(self, video_source, model_path: str, use_stream: bool = False):
        """
        Initializes the VideoPlayer GUI.

        Args:
            video_source (str or int): Path to the video file or device index/URL for a live stream.
            model_path (str): Path to the model weights.
            use_stream (bool, optional): If True, uses the StreamProcessor for live feeds.
                Otherwise, uses the VideoProcessor. Defaults to False.
        """
        super().__init__()

        # Set up the GUI components.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.video_label = QLabel()
        self.video_label.setScaledContents(True)
        self.layout.addWidget(self.video_label)

        # Initialize the appropriate video capture processor.
        if use_stream:
            self.video_processor = StreamProcessor(video_source)
        else:
            self.video_processor = VideoProcessor(video_source)

        # Create multiprocessing queues for inter-process communication.
        self.frame_queue = mp.Queue(maxsize=30)
        self.processed_queue = mp.Queue(maxsize=30)

        # Start the capture thread.
        self.capture_thread = threading.Thread(target=self.capture_frames, daemon=True)

        # Start the processing worker in a separate process.
        self.processing_process = mp.Process(
            target=process_frames_worker,
            args=(self.frame_queue, self.processed_queue, model_path),
            daemon=True,
        )

        # Timer to update the displayed frame at ~30 FPS.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(33)

        self.capture_thread.start()
        self.processing_process.start()

    def capture_frames(self):
        """Reads frames from the video or stream and adds them to the multiprocessing queue."""
        while True:
            frame = self.video_processor.get_frame()
            if frame is None:
                break
            try:
                self.frame_queue.put(frame, timeout=1)
            except queue.Full:
                continue

    def display_frame(self):
        """Displays the processed frame from the processed_queue on the GUI."""
        try:
            processed_frame = self.processed_queue.get_nowait()
        except queue.Empty:
            return

        frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        """Clean up resources when the window is closed."""
        self.video_processor.release()
        self.processing_process.terminate()
        self.processing_process.join()
        cv2.destroyAllWindows()
        super().closeEvent(event)
