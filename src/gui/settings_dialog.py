from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QDialog,
    QLabel,
    QComboBox,
    QDialogButtonBox,
    QWidget,
)
from PySide6.QtCore import QSettings, Signal, Slot


class SettingsDialog(QDialog):
    """Settings Modal Dialog"""

    settings_updated = Signal(str)  # Signal to notify about setting change

    MODEL_PATHS = {
        "Default": "/assets/default.py",
        "Lite (Faster)": "/assets/lite.pt",
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

        layout.addWidget(QLabel("Model:"))
        layout.addWidget(self.model_selection_combo)

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
        self.model_selection_combo.setCurrentText(model_name)

    @Slot()
    def save_settings(self):
        """Save settings using QSettings and emit signal for updates"""
        settings = QSettings("DroneTek", "DroneLink")
        selected_model = self.model_selection_combo.currentText()
        settings.setValue("model", selected_model)

        # Emit signal with the selected model's path
        self.settings_updated.emit(self.MODEL_PATHS[selected_model])
        self.accept()
