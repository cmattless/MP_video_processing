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
        Initializes the YOLO model and DeepSORT tracker.

        Args:
            model_path (str): Path to the YOLO model weights
            conf_threshold (float): Minimum confidence required to consider a detection.
            max_age (int): Maximum age parameter for DeepSORT.
            nn_budget (int): Budget for DeepSORT.
            nms_max_overlap (float): Maximum overlap for non-maximum suppression in DeepSORT.
            input_size (int): Input size for the model.
        """
        self.conf_threshold = conf_threshold
        self.input_size = input_size
        self.tracker = DeepSort(
            max_age=max_age, nn_budget=nn_budget, nms_max_overlap=nms_max_overlap
        )

        self.model = YOLO(model_path)

    def process_frame(self, frame):
        """
        Process a single frame: run detection with YOLO and track objects with DeepSORT.

        Args:
            frame (np.ndarray): The input video frame.

        Returns:
            list: A list of dictionaries containing bounding boxes ([x, y, w, h])
            and corresponding track IDs for confirmed tracks.
        """
        detections = []
        with torch.no_grad():
            results = self.model(frame)
        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy()
            for box, conf, cls in zip(boxes, confs, classes):
                if conf > self.conf_threshold:
                    x1, y1, x2, y2 = box
                    width, height = x2 - x1, y2 - y1
                    if width > 0 and height > 0:
                        detections.append(
                            ([x1, y1, width, height], float(conf), int(cls))
                        )

        tracked_objects = self.tracker.update_tracks(detections, frame=frame)
        return [
            {"bbox": track.to_ltwh(), "track_id": track.track_id}
            for track in tracked_objects
            if track.is_confirmed()
        ]
