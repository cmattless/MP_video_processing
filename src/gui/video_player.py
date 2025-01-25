from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer
import cv2
from core.video_processor import VideoProcessor
from core.model_processor import YOLODeepSortProcessor


class VideoPlayer(QMainWindow):
    def __init__(self, video_path: str, model_path: str):
        super().__init__()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.video_label = QLabel()
        self.video_label.setScaledContents(True)  # Scale the video to fit the label
        self.layout.addWidget(self.video_label)

        self.video_processor = VideoProcessor(video_path)
        self.processor = YOLODeepSortProcessor(model_path)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)  # 30 FPS (1000ms / 30 ≈ 33ms)

    def draw_bounding_boxes(self, img, tracked_objects):
        """Draw bounding boxes and IDs on the image."""
        for track in tracked_objects:
            x1, y1, x2, y2 = map(int, track["bbox"])
            track_id = track["track_id"]
            label = f"ID {track_id}"
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )

    def update_frame(self):
        frame = self.video_processor.get_frame()
        if frame is None:
            self.timer.stop()
            self.video_processor.release()
            return

        tracked_objects = self.processor.process_frame(frame)

        self.draw_bounding_boxes(frame, tracked_objects)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        """Release resources when the window is closed."""
        self.timer.stop()
        self.video_processor.release()
        cv2.destroyAllWindows()
        super().closeEvent(event)
