import os
import cv2
import numpy as np
import pytest

from src.core.archive_processor import ArchiveProcessor


@pytest.fixture
def temp_video_path(tmp_path):
    """Provides a path to a temp video file inside a non-existent directory."""
    output_dir = tmp_path / "nested" / "dir"
    output_file = output_dir / "test_video.mp4"
    return str(output_file)


def test_init_creates_output_directory_and_writer(temp_video_path):
    """
    GIVEN a non-existent output directory
    WHEN ArchiveProcessor is initialized
    THEN the directory should be created and the video writer opened successfully.
    """
    processor = ArchiveProcessor(output_path=temp_video_path, fps=1, frame_size=(2, 2))
    # The directory must now exist
    assert os.path.isdir(os.path.dirname(temp_video_path))
    # The VideoWriter must report as opened
    assert processor.video_writer.isOpened()
    processor.release()


def test_write_and_release_creates_valid_video_file(temp_video_path):
    """
    GIVEN an ArchiveProcessor and a single black frame
    WHEN write_frame and release are called
    THEN the output file should exist and contain at least one frame.
    """
    # Prepare a simple 2x2 black RGB frame
    frame = np.zeros((2, 2, 3), dtype=np.uint8)

    processor = ArchiveProcessor(output_path=temp_video_path, fps=1, frame_size=(2, 2))
    processor.write_frame(frame)
    processor.release()

    # File should exist and be non-empty
    assert os.path.isfile(temp_video_path)
    assert os.path.getsize(temp_video_path) > 0

    # Read back the video and verify frame count >= 1
    cap = cv2.VideoCapture(temp_video_path)
    assert cap.isOpened()
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    assert frame_count >= 1


def test_init_raises_io_error_when_video_writer_fails(monkeypatch, temp_video_path):
    """
    GIVEN that cv2.VideoWriter returns a writer that is not opened
    WHEN ArchiveProcessor is initialized
    THEN an IOError is raised.
    """

    class DummyBadWriter:
        def __init__(self, *args, **kwargs):
            pass

        def isOpened(self):
            return False

    # Monkeypatch VideoWriter and fourcc to use our dummy writer
    monkeypatch.setattr(cv2, "VideoWriter", DummyBadWriter)
    monkeypatch.setattr(cv2, "VideoWriter_fourcc", lambda *args, **kwargs: 0)

    with pytest.raises(IOError) as excinfo:
        ArchiveProcessor(output_path=temp_video_path)
    assert "Cannot open" in str(excinfo.value)
