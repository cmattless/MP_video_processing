# test_video_player.py
import pytest
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication
from src.gui.video_player import VideoPlayer


# Dummy video processor to simulate frames without an actual webcam.
class DummyVideoProcessor:
    def get_frame(self):
        # Return a black image (480x640 with 3 channels) as a dummy frame.
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def release(self):
        pass


# Monkey-patch the VideoPlayer to use the dummy video processor.
@pytest.fixture
def video_player(qtbot):
    player = VideoPlayer(0, model_path="dummy_model_path", use_stream=True)
    # Replace the real video_processor with our dummy version.
    player.video_processor = DummyVideoProcessor()
    qtbot.addWidget(player)
    player.show()
    yield player
    player.close()


def test_video_player_display(qtbot, video_player):
    """
    Test that the VideoPlayer displays frames.
    """
    # Wait a little to allow the timer to trigger display_frame
    qtbot.wait(1000)

    # Since our dummy returns a black image, we check that the pixmap exists.
    pixmap = video_player.video_label.pixmap()
    assert pixmap is not None, "No pixmap set on the video label."
