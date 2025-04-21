import numpy as np
import torch

import src.core.model_processor as model_module
from src.core.model_processor import Model

# --- Helpers for faking model outputs and tracker behavior ---


class FakeArray:
    """Simulates a torch tensor array with .cpu().numpy()."""

    def __init__(self, arr):
        self._arr = np.array(arr)

    def cpu(self):
        return self

    def numpy(self):
        return self._arr


class FakeBoxes:
    def __init__(self, xyxy, conf):
        self.xyxy = FakeArray(xyxy)
        self.conf = FakeArray(conf)


class FakeResult:
    def __init__(self, xyxy, conf):
        self.boxes = FakeBoxes(xyxy, conf)


class FakeTrack:
    def __init__(self, bbox, track_id, confirmed):
        self._bbox = bbox
        self.track_id = track_id
        self._confirmed = confirmed

    def to_ltwh(self):
        return self._bbox

    def is_confirmed(self):
        return self._confirmed


class FakeTracker:
    def __init__(self, max_age, nn_budget, nms_max_overlap):
        self.max_age = max_age
        self.nn_budget = nn_budget
        self.nms_max_overlap = nms_max_overlap
        self._tracks_to_return = []

    def update_tracks(self, detections, frame):
        # simply return whatever has been pre-set
        return self._tracks_to_return


# --- Tests ---


def test_init_sets_parameters_and_components(monkeypatch):
    """
    Model.__init__ should store params, build yolo_kwargs,
    and instantiate YOLO & DeepSort.
    """
    fake_yolo = object()

    def fake_yolo_ctor(path):
        assert path == "my_model.pt"
        return fake_yolo

    monkeypatch.setattr(model_module, "YOLO", fake_yolo_ctor)

    def fake_deepsort_ctor(max_age, nn_budget, nms_max_overlap):
        # verify args passed through correctly
        assert max_age == 15
        assert nn_budget == 50
        assert nms_max_overlap == 0.7
        return FakeTracker(max_age, nn_budget, nms_max_overlap)

    monkeypatch.setattr(model_module, "DeepSort", fake_deepsort_ctor)

    m = Model(
        model_path="my_model.pt",
        conf_threshold=0.25,
        max_age=15,
        nn_budget=50,
        nms_max_overlap=0.7,
        input_size=416,
    )

    # Check attributes
    assert m.conf_threshold == 0.25
    assert m.input_size == 416
    assert m.yolo_kwargs == {"conf": 0.25, "classes": [0], "imgsz": 416}
    # Check components set from our fakes
    assert m.model is fake_yolo
    assert isinstance(m.tracker, FakeTracker)
    assert m.tracker.max_age == 15
    assert m.tracker.nn_budget == 50
    assert m.tracker.nms_max_overlap == 0.7


def test_process_frame_returns_empty_when_no_detections(monkeypatch):
    """
    When YOLO returns no results and tracker has no tracks,
    process_frame should return [].
    """
    # patch YOLO to a function returning empty list
    monkeypatch.setattr(model_module, "YOLO", lambda path: (lambda frame,
                                                            **kwargs: []
                                                            ))
    # patch DeepSort to our FakeTracker
    fake_tracker = FakeTracker(10, 30, 1.0)
    monkeypatch.setattr(
        model_module,
        "DeepSort",
        lambda *args,
        **kwargs: fake_tracker
        )

    m = Model("dummy.pt")
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    output = m.process_frame(dummy_frame)
    assert output == []


def test_process_frame_filters_detections_and_tracks(monkeypatch):
    """
    process_frame should:
    - filter out detections below conf_threshold
    - filter out zero/negative-size boxes
    - return only confirmed tracks
    """

    # Prepare fake YOLO model function
    def fake_yolo(frame, **kwargs):
        # Three detections:
        # 1) valid: conf=0.6, w=2, h=2
        # 2) low confidence: conf=0.1, w=3, h=3
        # 3) zero-size: conf=0.9, w=0, h=0
        xyxy = [
            [0, 0, 2, 2],
            [5, 5, 8, 8],
            [10, 10, 10, 10],
        ]
        conf = [0.6, 0.1, 0.9]
        return [FakeResult(xyxy, conf)]

    monkeypatch.setattr(model_module, "YOLO", lambda path: fake_yolo)
    fake_tracker = FakeTracker(5, 20, 0.5)
    # Two tracks: one confirmed, one not
    fake_tracker._tracks_to_return = [
        FakeTrack([0, 0, 2, 2], track_id=42, confirmed=True),
        FakeTrack([5, 5, 3, 3], track_id=99, confirmed=False),
    ]
    monkeypatch.setattr(
        model_module,
        "DeepSort",
        lambda *args,
        **kwargs: fake_tracker
        )

    # Use a conf_threshold of 0.5 (filters out the 0.1 one)
    m = Model("dummy.pt", conf_threshold=0.5)
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    results = m.process_frame(dummy_frame)

    # Only the first detection is valid and its track is confirmed -> one entry
    assert results == [{"bbox": [0, 0, 2, 2], "track_id": 42}]


def test_torch_no_grad_context_applied(monkeypatch):
    """
    Ensure that process_frame uses torch.no_grad() context.
    We'll detect this by having the fake YOLO model raise if gradients enabled.
    """

    # fake YOLO that checks grad mode
    def fake_yolo(frame, **kwargs):
        assert not torch.is_grad_enabled()
        return []

    monkeypatch.setattr(model_module, "YOLO", lambda path: fake_yolo)
    monkeypatch.setattr(
        model_module,
        "DeepSort",
        lambda *args,
        **kwargs: FakeTracker(1, 1, 1.0)
    )

    m = Model("dummy.pt")
    # If torch.is_grad_enabled() is True inside the call, assertion fails
    _ = m.process_frame(np.zeros((10, 10, 3), dtype=np.uint8))
