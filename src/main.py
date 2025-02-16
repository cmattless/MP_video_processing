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

from gui.dialog_handler import DialogHandler
from gui.video_player import VideoPlayer
from gui.metadata_viewer import MetadataViewer
from gui.settings_dialog import SettingsDialog


class MainApp(QMainWindow):
    def __init__(self, model_key: str):
        super().__init__()
        self.setWindowTitle("DroneLink")
        self.model_key = model_key
        self.model_path = SettingsDialog.MODEL_PATHS.get(model_key, None)

        # Top widget with logo and menu bar in one horizontal layout
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # LOGO
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("./assets/DroneLink_light.png"))
        logo_label.setScaledContents(True)
        logo_label.setFixedHeight(15)
        logo_label.setFixedWidth(75)
        top_layout.addWidget(logo_label, alignment=Qt.AlignVCenter)

        # MENU BAR
        menubar = QMenuBar()
        self.file_menu = menubar.addMenu("File")
        self.open_action = QAction("Open", self)
        self.open_action.triggered.connect(self.__open_file)
        self.file_menu.addAction(self.open_action)

        # Disable the open action if no valid model path is set.
        self.open_action.setDisabled(self.model_path is None)

        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.__open_settings)
        settings_menu.addAction(settings_action)

        top_layout.addWidget(menubar, 1, alignment=Qt.AlignTop)
        self.setMenuWidget(top_widget)

        # Main layout: left side for video, right side for metadata
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Left frame for video footage
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: #2e2e2e; border-radius: 8px;")
        self.video_frame_layout = QVBoxLayout(self.video_frame)
        self.video_label = QLabel(f"Model Path: {self.model_path}")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_frame_layout.addWidget(self.video_label)
        self.main_layout.addWidget(self.video_frame, 2)

        # Right frame for metadata
        self.metadata_frame = QFrame()
        self.metadata_frame.setStyleSheet(
            "background-color: #2e2e2e; border-radius: 8px;"
        )
        self.metadata_frame_layout = QVBoxLayout(self.metadata_frame)
        self.meta_label = QLabel("Invalid Metadata")
        self.meta_label.setStyleSheet("color: white;")
        self.meta_label.setAlignment(Qt.AlignCenter)
        self.metadata_frame_layout.addWidget(self.meta_label)
        self.main_layout.addWidget(self.metadata_frame, 1)

        # Dialog Handler for file selection
        self.dialog_handler = DialogHandler(self)
        self.dialog_handler.signals.file_path_response.connect(
            self.__on_file_path_selected
        )

    def __open_file(self) -> None:
        """Trigger a file selection dialog to open a video file."""
        self.dialog_handler.request_file_path(
            title="Open Video File",
            file_filter="Video Files (*.mp4 *.avi *.mov);;All Files (*.*)",
            save_mode=False,
        )

    def __open_settings(self) -> None:
        """
        Open the settings dialog and update the model path.
        The dialog is expected to allow selection of a model key,
        which maps to an actual model path.
        """
        settings_dialog = SettingsDialog(self)
        settings_dialog.settings_updated.connect(self.update_model_path)
        if settings_dialog.exec():
            selected_key = settings_dialog.model_selection_combo.currentText()
            self.update_model_path(selected_key)

    @Slot(str)
    def update_model_path(self, new_key: str):
        """
        Update the model key and corresponding path.
        Also save the new key to QSettings and enable the file menu action.
        """
        if new_key in SettingsDialog.MODEL_PATHS:
            self.model_key = new_key
            self.model_path = SettingsDialog.MODEL_PATHS[new_key]
            settings = QSettings("DroneTek", "DroneLink")
            settings.setValue("model", self.model_key)
            self.video_label.setText(f"Model Path: {self.model_path}")
            self.open_action.setDisabled(False)
        else:
            self.open_action.setDisabled(True)

    @Slot(str)
    def __on_file_path_selected(self, file_path: str) -> None:
        """
        Handle the file path selected by the user.
        Instantiate and display a VideoPlayer if a valid file path is returned.
        """
        if file_path:
            self.meta_data = MetadataViewer(file_path)
            self.video_player = VideoPlayer(file_path, self.model_path)
            self.video_frame_layout.addWidget(self.video_player)
            self.video_frame_layout.removeWidget(self.video_label)

            self.metadata_frame_layout.addWidget(self.meta_data)
            self.metadata_frame_layout.removeWidget(self.meta_label)
        else:
            print("No file selected")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = QSettings("DroneTek", "DroneLink")
    # Retrieve the stored model key; default to "Default" if not set.
    model_key = settings.value("model", "Default")
    main_window = MainApp(model_key)
    main_window.showMaximized()
    main_window.show()
    sys.exit(app.exec())
