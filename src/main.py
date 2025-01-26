import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QWidget,
)
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Slot, Qt


# Import your DialogHandler (the signals-based version).
from gui.dialog_handler import DialogHandler
from gui.video_player import VideoPlayer


class MainApp(QMainWindow):
    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = model_path
        self.setWindowTitle("DroneLink")

        # Create a top-level widget to hold both the logo and the menu bar in one row.
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)  # remove layout margins

        # LOGO
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("./assets/DroneLink_light.png"))
        logo_label.setScaledContents(True)
        logo_label.setFixedHeight(15)
        logo_label.setFixedWidth(75)
        top_layout.addWidget(logo_label, alignment=Qt.AlignVCenter)

        # MENU BAR
        menubar = QMenuBar()
        file_menu = menubar.addMenu("File")
        openAction = QAction("Open", self)
        openAction.triggered.connect(self.__open_file)
        file_menu.addAction(openAction)
        top_layout.addWidget(menubar, 1, alignment=Qt.AlignTop)

        self.setMenuWidget(top_widget)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout: horizontal split -> Left side = video, Right side = metadata
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Create left frame for video footage
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: #2e2e2e; border-radius: 8px;")
        self.video_frame_layout = QVBoxLayout(self.video_frame)
        self.video_label = QLabel("No Video Input")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_frame_layout.addWidget(self.video_label)
        self.main_layout.addWidget(self.video_frame, 2)  # stretch factor 2

        # Create right frame for metadata
        self.metadata_frame = QFrame()
        self.metadata_frame.setStyleSheet(
            "background-color: #2e2e2e; border-radius: 8px;"
        )
        self.metadata_frame_layout = QVBoxLayout(self.metadata_frame)
        self.meta_label = QLabel("Invalid Metadata")
        self.meta_label.setStyleSheet("color: white;")  # Example text color
        self.meta_label.setAlignment(Qt.AlignCenter)
        self.metadata_frame_layout.addWidget(self.meta_label)
        self.main_layout.addWidget(self.metadata_frame, 1)

        self.dialog_handler = DialogHandler(self)
        self.dialog_handler.signals.file_path_response.connect(
            self.__on_file_path_selected
        )

    def __open_file(self) -> None:
        """
        Trigger a file selection dialog to open a video file. The actual file path
        is returned asynchronously through the 'on_file_path_selected' slot.
        """
        self.dialog_handler.request_file_path(
            title="Open Video File",
            file_filter="Video Files (*.mp4 *.avi *.mov);;All Files (*.*)",
            save_mode=False,
        )

    @Slot(str)
    def __on_file_path_selected(self, file_path: str) -> None:
        """
        Slot to handle the file path selected by the user. Instantiates and displays
        a VideoPlayer if a valid file path is returned.
        """
        if file_path:
            self.video_player = VideoPlayer(file_path, self.model_path)
            self.video_frame_layout.addWidget(self.video_player)
            self.video_frame_layout.removeWidget(self.video_label)
        else:
            print("No file selected")


if __name__ == "__main__":
    VIDEO_PATH = "../data/footage/drone_footage.mp4"
    MODEL_PATH = "./assets/best.pt"
    app = QApplication(sys.argv)
    main_window = MainApp(MODEL_PATH)
    main_window.showMaximized()
    main_window.show()
    sys.exit(app.exec())
