import cv2
import queue
import threading
import multiprocessing as mp
import time
from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

from core.video_processor import VideoProcessor
from core.stream_processor import StreamProcessor
from core.model_processor import Model
from src.core.video_utils.video_queue import VideoQueue


def draw_object_contours(img, tracked_objects):
    """
    For each detected object, draw a bounding box and label.
    """
    for track in tracked_objects:
        x, y, w, h = map(int, track["bbox"])
        # Ensure ROI is within image bounds
        if y < 0 or x < 0 or y + h > img.shape[0] or x + w > img.shape[1]:
            continue
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        label = f"ID {track['track_id']}"
        cv2.putText(
            img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
        )
    return img


def process_frames_worker(frame_queue, processed_queue, model_path, running_flag, n=3):
    """
    Process frames in a separate process. The worker continuously pulls frames
    from frame_queue, processes them using the model, draws contours, and puts
    the processed frame into processed_queue, skips nth frame (default 3).
    """
    model = Model(model_path)
    frame_counter = 0
    # Skip frames that are not the nth frame
    while running_flag.value:
        frame_counter += 1
        if frame_counter % n != 0:
            continue
        try:
            frame = frame_queue.get(timeout=0.05)
        except queue.Empty:
            continue

        tracked_objects = model.process_frame(frame)
        processed_frame = draw_object_contours(frame, tracked_objects)

        try:
            processed_queue.put(processed_frame, timeout=0.05)
        except queue.Full:
            # Skip frame if the processed queue is full to avoid blocking
            pass


class VideoPlayer(QMainWindow):
    def __init__(
        self, video_source, model_path: str, use_stream: bool = False, queue_size=100
    ):
        """
        Initializes the VideoPlayer GUI.

        Args:
            video_source (str or int): Video file path or stream source.
            model_path (str): Path to the model weights.
            use_stream (bool, optional): Use live stream processing if True.
            queue_size (int, optional): Maximum size of the inter-process queues.
        """
        super().__init__()
        self.running = True

        # Set up GUI components.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.video_label = QLabel()
        self.video_label.setScaledContents(True)
        self.layout.addWidget(self.video_label)

        # Initialize video capture processor.
        if use_stream:
            self.video_processor = StreamProcessor(video_source)
        else:
            self.video_processor = VideoProcessor(video_source)

        # Multiprocessing queues for frame exchange.
        self.frame_queue = mp.Queue(maxsize=queue_size)
        self.processed_queue = mp.Queue(maxsize=queue_size)
        # Shared flag for graceful shutdown.
        self.running_flag = mp.Value("b", True)

        # Start capture thread.
        self.capture_thread = threading.Thread(target=self.capture_frames, daemon=True)
        # Start the frame processing process.
        self.processing_process = mp.Process(
            target=process_frames_worker,
            args=(
                self.frame_queue,
                self.processed_queue,
                model_path,
                self.running_flag,
            ),
            daemon=True,
        )

        # Timer to update displayed frame (~30 FPS).
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(33)

        self.capture_thread.start()
        self.processing_process.start()

    def capture_frames(self):
        """
        Continuously capture frames from the video source and enqueue.
        """

        while self.running:
            frame = self.video_processor.get_frame()
            if frame is None:
                break

            try:
                self.frame_queue.put(frame, timeout=0.05)
            except queue.Full:
                continue

    def display_frame(self):
        """
        Dequeues and displays the latest processed frame. If multiple frames
        are waiting, skip to the most recent to minimize delay.
        """
        processed_frame = None
        while True:
            try:
                processed_frame = self.processed_queue.get_nowait()
            except queue.Empty:
                break

        if processed_frame is None:
            return

        # Convert color space and create QImage.
        frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        VideoQueue.enqueue(frame_rgb)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        """
        Cleanly shutdown threads, processes, and release resources on close.
        """
        self.running = False
        self.running_flag.value = False
        self.video_processor.release()
        self.processing_process.terminate()
        self.processing_process.join()
        cv2.destroyAllWindows()
        super().closeEvent(event)
