import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

# Load the trained YOLOv11 model
model = YOLO("./runs/detect/train3/weights/best.pt")

# Initialize DeepSORT tracker
tracker = DeepSort(max_age=30, nn_budget=70, nms_max_overlap=1.0)

# Open the video file
cap = cv2.VideoCapture("./data/footage/drone_footage.mp4")


def draw_bounding_boxes(img, tracked_objects):
    """Draw bounding boxes and IDs on the image."""
    for track in tracked_objects:
        x1, y1, x2, y2 = map(int, track["bbox"])
        track_id = track["track_id"]
        label = f"ID {track_id}"
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
        )


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform inference
    results = model(frame)

    # Extract YOLO detections
    detections = []
    for r in results:
        for box, confidence, cls in zip(r.boxes.xyxy, r.boxes.conf, r.boxes.cls):
            if model.names[int(cls.item())] == "person":  # Only track humans
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
    tracked_objects = tracker.update_tracks(bbox_xywh, confidences, frame)

    # Draw tracked objects
    draw_bounding_boxes(frame, tracked_objects)

    # Display the video with bounding boxes
    cv2.imshow("Drone Footage", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
