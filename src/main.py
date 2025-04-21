import sys
import cv2
import time
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QWidget,
    QInputDialog,
)
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Slot, Qt, QSettings
from PySide6.QtMultimedia import QMediaDevices

from core.video_utils.video_queue import VideoQueue
from core.archive_processor import ArchiveProcessor


from gui.dialog_handler import DialogHandler
from gui.video_player import VideoPlayer
from gui.metadata_viewer import MetadataViewer
from gui.settings_dialog import SettingsDialog


class MainApp(QMainWindow):
    def __init__(self, model_key: str, frame_skip: int = 3):
        super().__init__()
        self.setWindowTitle("DroneLink")

        self.archive_queue = VideoQueue()

        self.model_key = model_key
        self.frame_skip = frame_skip
        self.model_path = SettingsDialog.MODEL_PATHS.get(model_key, None)

        # Top widget with logo and menu bar in one horizontal layout
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # LOGO
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("./src/assets/DroneLink_light.png"))
        logo_label.setScaledContents(True)
        logo_label.setFixedHeight(15)
        logo_label.setFixedWidth(75)
        top_layout.addWidget(logo_label, alignment=Qt.AlignVCenter)

        # MENU BAR
        menubar = QMenuBar()
        self.file_menu = menubar.addMenu("File")

        self.export_action = QAction("Export", self)
        self.file_menu.addAction(self.export_action)
        self.export_action.triggered.connect(self.__export_video)

        self.open_action = QAction("Open", self)
        self.file_menu.addAction(self.open_action)
        self.open_action.triggered.connect(self.__open_file)

        self.connect_action = QAction("Connect", self)
        self.file_menu.addAction(self.connect_action)
        self.connect_action.triggered.connect(self.__connect_feed)

        self.file_menu.addAction("Exit").triggered.connect(self.close)

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

    def __export_video(self):
        """Export the video feed to a file."""
        if VideoQueue.is_empty():
            self.dialog_handler.show_message("No Video", "No video to export.")
            return

        # Use start_processors=False so that the __on_file_path_selected slot will return immediately.
        self.dialog_handler.request_file_path(
            title="Export Video",
            file_filter="Video Files (*.mp4);;All Files (*.*)",
            start_processors=False,
            save_mode=True,
        )
        # Connect export-specific slot
        self.dialog_handler.signals.file_path_response.connect(
            self._on_export_path_selected
        )

    def __open_file(self) -> None:
        """Trigger a file selection dialog to open a video file."""
        self.dialog_handler.request_file_path(
            title="Open Video File",
            file_filter="Video Files (*.mp4 *.avi *.mov);;All Files (*.*)",
            save_mode=False,
        )

    def get_available_video_devices(max_devices: int = 5) -> list:
        """
        Scans device indices from 0 to max_devices - 1 to find available video devices.

        Returns:
            list: A list of strings representing available devices (e.g., "Device 0").
        """
        available = []
        for i in range(max_devices):
            # Using CAP_DSHOW reduces spurious error messages on Windows.
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            # Allow a brief moment for initialization.
            time.sleep(0.1)
            if cap.isOpened():
                available.append(f"Device {i}")
            cap.release()
        print(available)
        return available

    @Slot(str)
    def __connect_feed(self) -> None:
        """Connect to the video feed by letting the user select from available devices."""
        cams = QMediaDevices.videoInputs()
        if not cams:
            self.dialog_handler.show_message(
                "No Devices", "No video devices available."
            )
            return

        # Build a list of human‑readable camera descriptions
        names = [cam.description() for cam in cams]
        chosen, ok = QInputDialog.getItem(
            self,
            "Select Camera",
            "Camera:",
            names,
            0,
            False,
        )
        if not ok:
            return

        # Map back to the integer index of the chosen camera
        idx = names.index(chosen)

        # Launch VideoPlayer exactly as before, with use_stream=True
        self.video_player = VideoPlayer(
            idx,
            self.archive_queue,
            self.model_path,
            use_stream=True,
            frame_skip=self.frame_skip,
        )
        self.video_frame_layout.addWidget(self.video_player)
        self.video_frame_layout.removeWidget(self.video_label)

    def __open_settings(self) -> None:
        """
        Open the settings dialog and update the model path.
        The dialog is expected to allow selection of a model key,
        which maps to an actual model path.
        """
        settings_dialog = SettingsDialog(self)
        settings_dialog.settings_updated.connect(self.update_model_path)
        settings_dialog.frame_skip_updated.connect(self.update_skipped_frames)
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

    @Slot()
    def update_skipped_frames(self, frame_skip: int) -> None:
        """
        Update the number of skipped frames for video processing.
        This is a placeholder for future functionality.
        """
        QSettings("DroneTek", "DroneLink").setValue("frame_skip", self.frame_skip)
        if hasattr(self, "video_player") and self.video_player is not None:
            self.video_player.set_frame_skip(self.frame_skip)

    @Slot(str)
    def __on_file_path_selected(
        self,
        file_path: str,
        start_processors: bool = False,
    ) -> None:
        """
        Handle the file path selected by the user.
        Instantiate and display a VideoPlayer if a valid file path is returned.
        """
        if not start_processors:
            return
        # Instantiate processors only when starting playback
        if file_path:
            self.meta_data = MetadataViewer(file_path)
            self.video_player = VideoPlayer(
                file_path,
                self.archive_queue,
                self.model_path,
                frame_skip=self.frame_skip,
            )
            self.video_frame_layout.addWidget(self.video_player)
            self.video_frame_layout.removeWidget(self.video_label)

            self.metadata_frame_layout.addWidget(self.meta_data)
            self.metadata_frame_layout.removeWidget(self.meta_label)
        else:
            print("No file selected")

    @Slot()
    def _on_video_closed(self):
        """
        Remove the metadata viewer and restore the default label
        when the video is closed.
        """
        if hasattr(self, "meta_data") and self.meta_data:
            self.metadata_frame_layout.removeWidget(self.meta_data)
            self.meta_data.deleteLater()
            self.meta_data = None
        # put the placeholder back
        self.metadata_frame_layout.addWidget(self.meta_label)

    @Slot(str)
    def _on_live_stream_selected(self, selection: str) -> None:
        """
        Handle the live stream selected by the user.
        Instantiate and display a VideoPlayer if a valid stream is returned.
        """
        if not selection:
            # User cancelled the selection.
            return
        device_index = int(selection.split()[-1])

        # self.meta_data = MetadataViewer("Live Stream")
        self.video_player = VideoPlayer(device_index, self.model_path, use_stream=True)
        self.video_frame_layout.addWidget(self.video_player)
        self.video_frame_layout.removeWidget(self.video_label)

        # self.metadata_frame_layout.addWidget(self.meta_data)
        # self.metadata_frame_layout.removeWidget(self.meta_label)

    @Slot(str)
    def _on_export_path_selected(self, file_path: str) -> None:
        """
        Handle the file path selected by the user for export.
        Instantiate and display an ArchiveProcessor if a valid file path is returned.
        """
        if not file_path:
            self.dialog_handler.show_message("Export Cancelled", "No file selected.")
            return

        # Close the video player if it exists to ensure resources are released.
        if hasattr(self, "video_player") and self.video_player is not None:
            self.video_player.close()

        queue_size = self.archive_queue.size()
        if queue_size == 0:
            self.dialog_handler.show_message(
                "Export Failed", "No frames available to export."
            )
            return

        # Create ArchiveProcessor and write frames
        archive_processor = ArchiveProcessor(file_path, 30, (640, 480))

        frames_exported = 0
        while not self.archive_queue.is_empty():
            frame = self.archive_queue.dequeue()
            if frame is not None:
                # Convert from RGB to BGR if needed.
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                # Resize frame to match the output video frame size.
                frame = cv2.resize(frame, (640, 480))
                archive_processor.write_frame(frame)
                frames_exported += 1

        archive_processor.release()

        if frames_exported > 0:
            self.dialog_handler.show_message(
                "Export Complete",
                f"Video exported successfully. Exported {frames_exported} frames.",
            )
        else:
            self.dialog_handler.show_message(
                "Export Failed", "Failed to export frames."
            )

        # Disconnect the export slot to avoid multiple connections if needed.
        self.dialog_handler.signals.file_path_response.disconnect(
            self._on_export_path_selected
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = QSettings("DroneTek", "DroneLink")
    # Retrieve the stored model key; default to "Default" if not set.
    model_key = settings.value("model", "Default")
    frame_skip = settings.value("frame_skip", 3)
    main_window = MainApp(model_key, frame_skip)
    main_window.showMaximized()
    main_window.show()
    sys.exit(app.exec())
