from PySide6.QtWidgets import QMainWindow, QScrollArea, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from core.metadata_processor import MetadataProcessor


class MetadataViewer(QMainWindow):

    def __init__(self, video_path: str):
        super().__init__()
        self.setWindowTitle("Metadata Viewer")

        self.metadata_processor = MetadataProcessor(video_path)
        general_info, video_info, audio_info = self.metadata_processor.get_metadata()

        self.scroll_area = QScrollArea()
        self.central_widget = QWidget()

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.central_widget)

        self.setCentralWidget(self.scroll_area)
        self.layout = QVBoxLayout(self.central_widget)

        self.general_label = QLabel(f"General Information:\n{general_info}")
        self.video_label = QLabel(f"Video Information:\n{video_info}")
        self.audio_label = QLabel(f"Audio Information:\n{audio_info}")

        self.layout.addWidget(self.general_label)
        self.layout.addWidget(self.video_label)
        self.layout.addWidget(self.audio_label)
