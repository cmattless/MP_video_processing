from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort


class Model:
    def __init__(self, model_path: str, max_age=30, nn_budget=70, nms_max_overlap=1.0):
        self.model = YOLO(model_path)
        self.tracker = DeepSort(
            max_age=max_age, nn_budget=nn_budget, nms_max_overlap=nms_max_overlap
        )

    def process_frame(self, frame):
        """Process a frame through YOLO and DeepSORT."""
        results = self.model(frame)

        # Prepare detections in the format expected by DeepSORT
        bbs = []
        for r in results:
            for box, confidence, cls in zip(r.boxes.xyxy, r.boxes.conf, r.boxes.cls):
                x1, y1, x2, y2 = box.cpu().numpy()  # Bounding box coordinates
                width, height = x2 - x1, y2 - y1
                if (
                    confidence > 0.5 and width > 0 and height > 0
                ):  # Filter low-confidence and invalid detections
                    bbs.append(
                        ([x1, y1, width, height], confidence.item(), int(cls.item()))
                    )

        # Update tracker
        tracked_objects = self.tracker.update_tracks(bbs, frame=frame)

        # Return tracked objects
        return [
            {
                "bbox": track.to_ltwh(),  # Convert bounding box to [left, top, width, height]
                "track_id": track.track_id,
            }
            for track in tracked_objects
            if track.is_confirmed()
        ]
