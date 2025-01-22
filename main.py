import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from src.gui.video_player import VideoPlayer


class MainApp(QMainWindow):
    def __init__(self, video_path: str, model_path: str):
        super().__init__()
        self.setWindowTitle("Modular Drone Footage Tracker")
        self.setGeometry(100, 100, 1024, 768)

        # Central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout for the central widget
        layout = QVBoxLayout(central_widget)

        # VideoPlayer widget
        self.video_player = VideoPlayer(video_path, model_path)

        # Add VideoPlayer to the layout
        layout.addWidget(self.video_player)


if __name__ == "__main__":
    VIDEO_PATH = "./data/footage/drone_footage.mp4"
    MODEL_PATH = "./runs/detect/train3/weights/best.pt"

    app = QApplication(sys.argv)

    # Main application window
    main_window = MainApp(VIDEO_PATH, MODEL_PATH)
    main_window.show()

    sys.exit(app.exec())
