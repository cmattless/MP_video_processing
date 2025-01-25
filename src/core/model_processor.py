from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

class YOLODeepSortProcessor:
    def __init__(self, model_path: str, max_age=30, nn_budget=70, nms_max_overlap=1.0):
        self.model = YOLO(model_path)
        self.tracker = DeepSort(max_age=max_age, nn_budget=nn_budget, nms_max_overlap=nms_max_overlap)

    def process_frame(self, frame):
        """Process a frame through YOLO and DeepSORT."""
        results = self.model(frame)

        # Extract YOLO detections
        detections = []
        for r in results:
            for box, confidence, cls in zip(r.boxes.xyxy, r.boxes.conf, r.boxes.cls):
                if self.model.names[int(cls.item())] == "person":  # Only track humans
                    detections.append(
                        {
                            "bbox": box.cpu().numpy().tolist(),
                            "confidence": confidence.item(),
                        }
                    )

        # Convert detections for DeepSORT
        bbox_xywh = []
        confidences = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            bbox_xywh.append([x1, y1, x2 - x1, y2 - y1])  # Convert to [x, y, w, h]
            confidences.append(det["confidence"])

        # Update tracker
        tracked_objects = self.tracker.update_tracks(bbox_xywh, confidences, frame)
        return tracked_objects
