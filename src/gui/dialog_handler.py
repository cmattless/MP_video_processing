# Updated DialogHandler with drop-down support
from PySide6.QtWidgets import QMessageBox, QFileDialog, QInputDialog, QWidget
from PySide6.QtCore import QObject, Signal


class DialogSignals(QObject):
    message_shown = Signal(str, str)
    yes_no_asked = Signal(str, str)
    file_path_requested = Signal(str, str, bool)
    text_input_requested = Signal(str, str, str)
    item_selection_requested = Signal(str, str, list)

    yes_no_response = Signal(bool)
    file_path_response = Signal(str)
    text_input_response = Signal(str)
    item_selection_response = Signal(str)


class DialogHandler:
    """
    Centralized handler for message, confirmation, file selection, text input, and
    item selection dialogs using signals for better decoupling.
    """

    def __init__(self, parent: QWidget = None) -> None:
        self.signals = DialogSignals()
        self.parent = parent

        self.signals.message_shown.connect(self._handle_message)
        self.signals.yes_no_asked.connect(self._handle_yes_no)
        self.signals.file_path_requested.connect(self._handle_file_path)
        self.signals.text_input_requested.connect(self._handle_text_input)
        self.signals.item_selection_requested.connect(self._handle_item_selection)

    def _handle_message(self, title: str, message: str) -> None:
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def _handle_yes_no(self, title: str, message: str) -> None:
        reply = QMessageBox.question(
            self.parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        self.signals.yes_no_response.emit(reply == QMessageBox.StandardButton.Yes)

    def _handle_file_path(self, title: str, file_filter: str, save_mode: bool) -> None:
        if save_mode:
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent, title, "", file_filter
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self.parent, title, "", file_filter
            )
        self.signals.file_path_response.emit(file_path)

    def _handle_text_input(self, title: str, message: str, default_text: str) -> None:
        text, ok = QInputDialog.getText(self.parent, title, message, text=default_text)
        self.signals.text_input_response.emit(text if ok else "")

    def _handle_item_selection(self, title: str, message: str, items: list) -> None:
        # Display a drop-down list for item selection.
        if items:
            item, ok = QInputDialog.getItem(
                self.parent, title, message, items, 0, False
            )
            if ok:
                self.signals.item_selection_response.emit(item)
            else:
                self.signals.item_selection_response.emit("")
        else:
            self.signals.item_selection_response.emit("")

    def show_message(self, title: str, message: str) -> None:
        self.signals.message_shown.emit(title, message)

    def ask_yes_no(self, title: str, message: str) -> None:
        self.signals.yes_no_asked.emit(title, message)

    def request_file_path(
        self, title: str, file_filter: str = "All Files (*.*)", save_mode: bool = False
    ) -> None:
        self.signals.file_path_requested.emit(title, file_filter, save_mode)

    def request_text_input(
        self, title: str, message: str, default_text: str = ""
    ) -> None:
        self.signals.text_input_requested.emit(title, message, default_text)

    def ask_item(self, title: str, message: str, items: list) -> None:
        self.signals.item_selection_requested.emit(title, message, items)
