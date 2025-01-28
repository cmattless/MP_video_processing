import threading
import queue
import time
import cv2

from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

from core.video_processor import VideoProcessor
from core.model_processor import Model


class VideoPlayer(QMainWindow):
    def __init__(self, video_path: str, model_path: str):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.video_label = QLabel()
        self.video_label.setScaledContents(True)
        self.layout.addWidget(self.video_label)

        self.video_processor = VideoProcessor(video_path)
        self.processor = Model(model_path)

        self.frame_queue = queue.Queue(maxsize=10)
        self.processed_frame = None

        self.capture_thread = threading.Thread(target=self.capture_frames, daemon=True)
        self.processing_thread = threading.Thread(
            target=self.process_frames, daemon=True
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(33)  # ~30 FPS playback

        self.capture_thread.start()
        self.processing_thread.start()

    def capture_frames(self):
        """Reads frames from the video and adds them to the queue."""
        while True:
            frame = self.video_processor.get_frame()
            if frame is None:
                break 
            try:
                self.frame_queue.put(frame, timeout=1) 
            except queue.Full:
                continue 
    def process_frames(self):
        """Processes frames from the queue and updates the processed frame."""
        while True:
            try:
                frame = self.frame_queue.get(timeout=1)
                tracked_objects = self.processor.process_frame(frame)
                self.processed_frame = self.draw_bounding_boxes(frame, tracked_objects)
            except queue.Empty:
                continue 

    def draw_bounding_boxes(self, img, tracked_objects):
        """Draw bounding boxes and IDs on the image."""
        for track in tracked_objects:
            x, y, w, h = map(int, track["bbox"]) 
            track_id = track["track_id"]
            label = f"ID {track_id}"
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        return img

    def display_frame(self):
        """Displays the processed frame on the GUI."""
        if self.processed_frame is not None:
            frame_rgb = cv2.cvtColor(self.processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        """Release resources when the window is closed."""
        self.video_processor.release()
        cv2.destroyAllWindows()
        super().closeEvent(event)
