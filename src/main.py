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
from PySide6.QtCore import Slot, Qt, QSettings

# Import DialogHandler, VideoPlayer, and SettingsDialog
from gui.dialog_handler import DialogHandler
from gui.video_player import VideoPlayer
from gui.settings_dialog import SettingsDialog


class MainApp(QMainWindow):
    def __init__(self, model_path: str):
        super().__init__()
        self.setWindowTitle("DroneLink")
        self.model_path = model_path  # Store the initial model path

        # Create a top-level widget to hold both the logo and the menu bar in one row.
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins

        # LOGO
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("./assets/DroneLink_light.png"))
        logo_label.setScaledContents(True)
        logo_label.setFixedHeight(15)
        logo_label.setFixedWidth(75)
        top_layout.addWidget(logo_label, alignment=Qt.AlignVCenter)

        # MENU BAR
        menubar = QMenuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        self.open_action = QAction("Open", self)
        self.open_action.triggered.connect(self.__open_file)
        file_menu.addAction(self.open_action)

        # Disable file menu if model path is not set
        file_menu.setDisabled(self.model_path is None)

        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.__open_settings)
        settings_menu.addAction(settings_action)

        top_layout.addWidget(menubar, 1, alignment=Qt.AlignTop)
        self.setMenuWidget(top_widget)

        # Main layout: horizontal split -> Left side = video, Right side = metadata
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Create left frame for video footage
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: #2e2e2e; border-radius: 8px;")
        self.video_frame_layout = QVBoxLayout(self.video_frame)
        self.video_label = QLabel(f"Model Path: {self.model_path}")
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

        # Dialog Handler for File Selection
        self.dialog_handler = DialogHandler(self)
        self.dialog_handler.signals.file_path_response.connect(
            self.__on_file_path_selected
        )

    def __open_file(self) -> None:
        """
        Trigger a file selection dialog to open a video file.
        """
        self.dialog_handler.request_file_path(
            title="Open Video File",
            file_filter="Video Files (*.mp4 *.avi *.mov);;All Files (*.*)",
            save_mode=False,
        )

    def __open_settings(self) -> None:
        """
        Open the settings dialog and update the model path when changed.
        """
        settings_dialog = SettingsDialog(self)
        settings_dialog.settings_updated.connect(
            self.update_model_path
        )  # Connect signal
        if settings_dialog.exec():
            self.update_model_path(
                settings_dialog.MODEL_PATHS.get(
                    settings_dialog.model_selection_combo.currentText(), None
                )
            )

    @Slot(str)
    def update_model_path(self, new_path: str):
        """
        Update the model path dynamically when settings change.
        """
        if new_path:
            self.model_path = new_path
            settings = QSettings("DroneTek", "DroneLink")
            settings.setValue("model", self.model_path)

            # Update UI elements
            self.video_label.setText(f"Model Path: {self.model_path}")
            self.open_action.setDisabled(False)  # Enable file menu
        else:
            self.open_action.setDisabled(True)  # Disable file menu if no model is set

    @Slot(str)
    def __on_file_path_selected(self, file_path: str) -> None:
        """
        Slot to handle the file path selected by the user. Instantiates and displays
        a VideoPlayer if a valid file path is returned.
        """
        if file_path:
            self.meta_data = None
            self.video_player = VideoPlayer(file_path, self.model_path)
            self.video_frame_layout.addWidget(self.video_player)
            self.video_frame_layout.removeWidget(self.video_label)
        else:
            print("No file selected")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load the stored model path
    settings = QSettings("DroneTek", "DroneLink")
    model_name = settings.value("model", "Default")
    model_path = SettingsDialog.MODEL_PATHS.get(model_name, None)

    # Launch the application
    main_window = MainApp(model_path)
    main_window.showMaximized()
    main_window.show()

    sys.exit(app.exec())
