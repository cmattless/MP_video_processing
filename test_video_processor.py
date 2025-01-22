import pytest
from video_processor import VideoProcessor

def test_video_processor_initialization():
    vp = VideoProcessor("./data/footage/drone_footage.mp4")
    assert vp.cap.isOpened() is False  # Replace with a valid video path for real tests
