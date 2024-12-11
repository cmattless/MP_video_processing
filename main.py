import cv2
from ultralytics import YOLO

# Load the trained YOLOv11 model
model = YOLO('./runs/detect/train6/weights/best.pt')

# Open the video file
cap = cv2.VideoCapture('./data/footage/drone_footage.mp4')

def draw_bounding_boxes(img, detections):
    """Draw bounding boxes on the image."""
    for detection in detections:
        x1, y1, x2, y2 = map(int, detection['box'])
        label = f"{detection['name']} {detection['confidence']:.2f}"
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform inference
    results = model(frame)

    # Extract detections
    detections = []
    for r in results:
        for box, confidence, cls in zip(r.boxes.xyxy, r.boxes.conf, r.boxes.cls):
            detections.append({
                "box": box.cpu().numpy().tolist(),
                "confidence": confidence.item(),
                "name": model.names[int(cls.item())]
            })

    # Draw bounding boxes
    draw_bounding_boxes(frame, detections)

    # Display the video with bounding boxes
    cv2.imshow("Drone Footage", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
