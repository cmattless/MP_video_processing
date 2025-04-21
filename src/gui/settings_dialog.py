import os
from PySide6.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QLabel,
    QComboBox,
    QDialogButtonBox,
)
from PySide6.QtCore import QSettings, Signal, Slot


class SettingsDialog(QDialog):
    """Settings Modal Dialog"""

    settings_updated = Signal(str)  # Signal to notify about setting change
    frame_skip_updated = Signal(int)
    # search assets folder for model files and return the paths
    assets = os.listdir(
        os.path.abspath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets")
        )
    )
    assets = [asset for asset in assets if asset.endswith(".pt")]

    MODEL_PATHS = {
        asset: os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "..", "assets", asset
            )
        )
        for asset in assets
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedSize(300, 200)

        # Layout
        layout = QVBoxLayout(self)

        self.model_selection_combo = QComboBox(self)
        self.model_selection_combo.addItems(self.MODEL_PATHS.keys())

        self.frame_skip_combo = QComboBox(self)
        self.frame_skip_combo.addItems([str(i) for i in range(1, 11)])

        layout.addWidget(QLabel("Model:"))
        layout.addWidget(self.model_selection_combo)

        layout.addWidget(
            QLabel("Number of skipped frames (Higher = better performance):")
        )
        layout.addWidget(self.frame_skip_combo)

        # Dialog Buttons (Save/Cancel)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel, self
        )
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

        self.load_settings()

    def load_settings(self):
        """Load settings from QSettings"""
        settings = QSettings("DroneTek", "DroneLink")
        model_name = settings.value("model", "Default")
        frame_skip = settings.value("frame_skip", 1)
        self.frame_skip_combo.setCurrentText(str(frame_skip))
        self.model_selection_combo.setCurrentText(model_name)

    @Slot()
    def save_settings(self):
        """Save settings using QSettings and emit signal for updates"""
        settings = QSettings("DroneTek", "DroneLink")
        selected_model = self.model_selection_combo.currentText()
        frame_skip = int(self.frame_skip_combo.currentText())
        settings.setValue("frame_skip", frame_skip)
        settings.setValue("model", selected_model)

        self.settings_updated.emit(selected_model)
        self.frame_skip_updated.emit(frame_skip)
        self.accept()
