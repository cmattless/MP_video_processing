from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import torch

class Model:
    def __init__(
        self,
        model_path: str,
        conf_threshold: float = 0.2,
        max_age: int = 10,
        nn_budget: int = 30,
        nms_max_overlap: float = 1.0,
        input_size: int = 640,
    ):
        """
        Initializes the YOLO model (filtered to only class 0 == 'person')
        and DeepSORT tracker.
        """
        self.conf_threshold = conf_threshold
        self.input_size = input_size

        # tell YOLO to only detect class 0 (person)
        self.yolo_kwargs = {
            "conf": self.conf_threshold,
            "classes": [0],
            "imgsz": self.input_size,
        }

        self.model = YOLO(model_path)
        self.tracker = DeepSort(
            max_age=max_age,
            nn_budget=nn_budget,
            nms_max_overlap=nms_max_overlap,
        )

    def process_frame(self, frame):
        """
        Process a single frame: run detection with YOLO and track objects with DeepSORT.

        Args:
            frame (np.ndarray): The input video frame.

        Returns:
            list: A list of dictionaries containing bounding boxes ([x, y, w, h])
            and corresponding track IDs for confirmed tracks.
        """
        # run inference with class‐filtering baked in
        with torch.no_grad():
            results = self.model(frame, **self.yolo_kwargs)

        detections = []
        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            # all classes in "r" will be 0, so we can skip checking cls
            for (x1, y1, x2, y2), conf in zip(boxes, confs):
                if conf < self.conf_threshold:
                    continue
                w, h = x2 - x1, y2 - y1
                if w <= 0 or h <= 0:
                    continue
                detections.append(
                    ([x1, y1, w, h], float(conf), 0)
                )

        tracks = self.tracker.update_tracks(detections, frame=frame)
        return [
            {"bbox": track.to_ltwh(), "track_id": track.track_id}
            for track in tracks
            if track.is_confirmed()
        ]
