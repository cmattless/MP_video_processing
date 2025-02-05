# video_player.py

import cv2
import queue
import threading
import multiprocessing as mp
from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

from core.video_processor import VideoProcessor
from core.model_processor import Model


def draw_bounding_boxes(img, tracked_objects):
    """
    Draw bounding boxes and track IDs on the image.

    Args:
        img (np.ndarray): The image on which to draw.
        tracked_objects (list): List of tracked object dictionaries.

    Returns:
        np.ndarray: Image with drawn bounding boxes and IDs.
    """
    for track in tracked_objects:
        x, y, w, h = map(int, track["bbox"])
        track_id = track["track_id"]
        label = f"ID {track_id}"
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            img,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )
    return img


def process_frames_worker(frame_queue, processed_queue, model_path, use_onnx):
    """
    Process frames in a separate process.

    Initializes the model and continuously pulls frames from frame_queue,
    processes them, draws bounding boxes, and pushes the processed frame
    to processed_queue.
    """
    model = Model(model_path, use_onnx=use_onnx)
    while True:
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        tracked_objects = model.process_frame(frame)
        processed_frame = draw_bounding_boxes(frame, tracked_objects)
        processed_queue.put(processed_frame)


class VideoPlayer(QMainWindow):
    def __init__(self, video_path: str, model_path: str, use_onnx: bool = False):
        """
        Initializes the VideoPlayer GUI.

        Args:
            video_path (str): Path to the video file.
            model_path (str): Path to the YOLO model weights or ONNX model.
            use_onnx (bool): If True, uses ONNX Runtime for inference.
        """
        super().__init__()

        # Set up the GUI components.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.video_label = QLabel()
        self.video_label.setScaledContents(True)
        self.layout.addWidget(self.video_label)

        # Initialize video capture.
        self.video_processor = VideoProcessor(video_path)

        # Create multiprocessing queues for inter-process communication.
        self.frame_queue = mp.Queue(maxsize=30)
        self.processed_queue = mp.Queue(maxsize=30)

        # Start the capture thread in the main process.
        self.capture_thread = threading.Thread(target=self.capture_frames, daemon=True)

        # Start the processing worker as a separate process.
        self.processing_process = mp.Process(
            target=process_frames_worker,
            args=(self.frame_queue, self.processed_queue, model_path, use_onnx),
            daemon=True,
        )

        # Timer to update the displayed frame at ~30 FPS.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(33)

        self.capture_thread.start()
        self.processing_process.start()

    def capture_frames(self):
        """Reads frames from the video and adds them to the multiprocessing queue."""
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

        # Convert BGR frame to RGB and display.
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
