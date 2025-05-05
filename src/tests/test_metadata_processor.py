import json
import pytest
from pymediainfo import MediaInfo

from src.core.metadata_processor import MetadataProcessor

# Helper track dicts
GENERAL_TRACK = {
    "track_type": "General",
    "title": "Test File",
    "duration": "1234"
}
VIDEO_TRACK = {
    "track_type": "Video",
    "format": "AVC",
    "width": "1920",
    "height": "1080",
}
AUDIO_TRACK = {"track_type": "Audio", "format": "AAC", "channels": "2"}


class FakeMediaInfo:
    def __init__(self, data):
        self._data = data

    def to_data(self):
        return self._data

    @staticmethod
    def parse(file_path):
        # placeholder; will be monkeypatched per-test
        raise RuntimeError("Should be monkeypatched")


@pytest.fixture(autouse=True)
def patch_mediainfo(monkeypatch):
    """
    Patch MediaInfo.parse to use FakeMediaInfo.
    Individual tests will set monkeypatch parse to return the desired data.
    """
    monkeypatch.setattr(MediaInfo, "parse", FakeMediaInfo.parse)
    yield


def make_fake_parse(data, counter: dict = None):
    """
    Returns a fake parse function that returns FakeMediaInfo(data)
    and optionally increments counter['n'] on each call.
    """

    def _fake_parse(path):
        if counter is not None:
            counter["n"] += 1
        return FakeMediaInfo(data)

    return _fake_parse


def test_get_metadata_all_tracks(monkeypatch):
    """
    get_metadata should return JSON strings for
    General, Video, and Audio tracks.
    """
    data = {"tracks": [GENERAL_TRACK, VIDEO_TRACK, AUDIO_TRACK]}
    monkeypatch.setattr(MediaInfo, "parse", make_fake_parse(data))

    mp = MetadataProcessor("dummy.mp4")
    general_json, video_json, audio_json = mp.get_metadata()

    # Parse back to dict for assertion
    assert json.loads(general_json) == GENERAL_TRACK
    assert json.loads(video_json) == VIDEO_TRACK
    assert json.loads(audio_json) == AUDIO_TRACK


@pytest.mark.parametrize(
    "tracks,expected",
    [
        ([], (None, None, None)),
        ([GENERAL_TRACK], (GENERAL_TRACK, None, None)),
        ([VIDEO_TRACK], (None, VIDEO_TRACK, None)),
        ([AUDIO_TRACK], (None, None, AUDIO_TRACK)),
        ([GENERAL_TRACK, AUDIO_TRACK], (GENERAL_TRACK, None, AUDIO_TRACK)),
    ],
)
def test_get_metadata_missing_tracks(monkeypatch, tracks, expected):
    """
    get_metadata should correctly return None for missing track types,
    and JSON strings for present ones.
    """
    data = {"tracks": tracks}
    monkeypatch.setattr(MediaInfo, "parse", make_fake_parse(data))

    mp = MetadataProcessor("file")
    general_json, video_json, audio_json = mp.get_metadata()

    # Convert JSON back to dict or None
    result = tuple(
        json.loads(s) if isinstance(s, str) else None
        for s in (general_json, video_json, audio_json)
    )
    assert result == expected


def test_parse_called_only_once(monkeypatch):
    """
    Calling get_metadata multiple times
    should only invoke MediaInfo.parse once.
    """
    data = {"tracks": [GENERAL_TRACK]}
    counter = {"n": 0}
    monkeypatch.setattr(MediaInfo, "parse", make_fake_parse(data, counter))

    mp = MetadataProcessor("dup.mp4")
    # First call: parse invoked
    mp.get_metadata()
    # Second call: data already present, parse should not be invoked again
    mp.get_metadata()
    assert counter["n"] == 1


def test_private_getters_direct(monkeypatch):
    """
    Test the private __get_* methods directly by setting mp.data manually.
    """
    mp = MetadataProcessor("ignored")
    # Case: only video track
    mp.data = {"tracks": [VIDEO_TRACK]}
    # Access private methods via name mangling
    gen = mp._MetadataProcessor__get_general_info()
    vid = mp._MetadataProcessor__get_video_info()
    aud = mp._MetadataProcessor__get_audio_info()
    assert gen is None
    assert json.loads(vid) == VIDEO_TRACK
    assert aud is None

    # Case: no tracks
    mp.data = {"tracks": []}
    assert mp._MetadataProcessor__get_general_info() is None
    assert mp._MetadataProcessor__get_video_info() is None
    assert mp._MetadataProcessor__get_audio_info() is None
