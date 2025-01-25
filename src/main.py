import sys
from PySide6.QtWidgets import QApplication, QMainWindow,QMenuBar, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QPixmap, QAction
from src.gui.video_player import VideoPlayer


class MainApp(QMainWindow):
    def __init__(self, video_path: str, model_path: str):
        super().__init__()
        self.video_path = video_path
        self.model_path = model_path
        self.setWindowTitle("DroneLink")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

        wordmark_label = QLabel()
        wordmark_label.setPixmap(QPixmap("./assets/DroneLink_light.png"))

        menu = QMenuBar()
        menu.addMenu("File")

        openAction = QAction("Open", self)
        openAction.triggered.connect(self.open_file)


    def open_file(self):
        self.video_player = VideoPlayer(self.video_path, self.model_path)
        self.layout.addWidget(self.video_player)

if __name__ == "__main__":
    VIDEO_PATH = "./data/footage/drone_footage.mp4"
    MODEL_PATH = "./runs/detect/train3/weights/best.pt"
    app = QApplication(sys.argv)
    main_window = MainApp(VIDEO_PATH, MODEL_PATH)
    main_window.showMaximized()
    main_window.show()

