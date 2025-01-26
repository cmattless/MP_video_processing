from PySide6.QtWidgets import QMessageBox, QFileDialog, QInputDialog, QWidget
from PySide6.QtCore import Qt


class DialogHandler:
    @staticmethod
    def show_message(
        title: str,
        message: str,
        icon: QMessageBox.Icon = QMessageBox.Icon.Information,
        parent: QWidget = None,
    ) -> None:
        """Display a message dialog with OK button."""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    @staticmethod
    def show_yes_no_dialog(title: str, message: str) -> bool:
        """
        Display a Yes/No dialog and return True for Yes, False for No.
        """
        reply = QMessageBox.question(
            None,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    @staticmethod
    def get_file_path(
        title: str, file_filter: str = "All Files (*.*)", save_mode: bool = False
    ) -> str:
        """
        Open a file dialog and return the selected file path.
        If save_mode is True, opens a Save File dialog instead of Open File dialog.
        """
        if save_mode:
            file_path, _ = QFileDialog.getSaveFileName(None, title, "", file_filter)
        else:
            file_path, _ = QFileDialog.getOpenFileName(None, title, "", file_filter)
        return file_path

    @staticmethod
    def get_text_input(title: str, message: str, default_text: str = "") -> str:
        """
        Display an input dialog and return the entered text.
        Returns empty string if canceled.
        """
        text, ok = QInputDialog.getText(None, title, message, text=default_text)
        return text if ok else ""
