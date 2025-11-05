# backend/yolov8_inference.py

import os
import yaml
import cv2
import base64
import numpy as np
from ultralytics import YOLO
from backend.utils  import draw_neon_corner_box  

# Load configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
yaml_path = os.path.join(BASE_DIR, "inference_phams.yaml")

with open(yaml_path, "r") as f:
    params = yaml.safe_load(f)

traind_model_path = os.path.join(BASE_DIR, "model/best.pt")

# Load YOLO model
model_path = traind_model_path
model = YOLO(model_path)
class_list = model.names

# --------------------------------------------------
# Main Inference Function
# --------------------------------------------------
def process_egg_tray(image_bytes: bytes):
    """
    Perform YOLO inference on uploaded egg tray image.
    Counts eggs & empty slots, draws glowing corner boxes,
    and returns annotated image + metrics as JSON.
    """

    # Convert image bytes → numpy array
    image_array = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Invalid image data received.")

    # Run YOLO inference
    results = model.predict(
        source=frame,
        conf=params.get("confidence_threshold", 0.5),
        classes=params.get("classes_to_track", None),
        verbose=False
    )

    # Initialize counts
    num_eggs = 0
    num_empty_slots = 0

    # Draw neon corner boxes
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            cls_name = class_list[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            # Choose color
            if cls_name.lower() == "egg":
                color = (0, 255, 0)       # Neon Green
                num_eggs += 1
            else:
                color = (0, 0, 255)       # Neon Red
                num_empty_slots += 1

            # Draw custom glowing corner box
            frame = draw_neon_corner_box(frame, x1, y1, x2, y2, color=color, thickness=2, corner_len=20, glow_intensity=0.3)

            # Add label above box
            cv2.putText(frame, f"{cls_name} {conf:.2f}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Determine tray status
    tray_status = "OK" if num_empty_slots == 0 else "Not OK"

    # Overlay summary text in a more aesthetic way
    status_text = f"Tray: {tray_status}"
    status_color_bgr = (0, 255, 0) if tray_status == "OK" else (0, 0, 255)  # green/red
    text_color = (255, 255, 255)

    # Choose font (using Hershey but close to Times New Roman feel)
    font = cv2.FONT_HERSHEY_COMPLEX

    # Calculate text size to draw rectangle neatly around it
    (text_width, text_height), baseline = cv2.getTextSize(status_text, font, 1, 2)
    rect_x, rect_y = 30, 30
    rect_w, rect_h = text_width + 40, text_height + 20

    # Draw filled rectangle for status background
    cv2.rectangle(frame, (rect_x, rect_y - text_height - 10),
                (rect_x + rect_w, rect_y + 10), status_color_bgr, -1)

    # Put white text on top of rectangle
    cv2.putText(frame, status_text, (rect_x + 15, rect_y),
                font, 1, text_color, 2, cv2.LINE_AA)


    # Convert annotated image → base64 for frontend
    _, buffer = cv2.imencode(".jpg", frame)
    encoded_image = base64.b64encode(buffer).decode("utf-8")

    # Construct response
    return {
        "num_eggs": num_eggs,
        "num_empty_slots": num_empty_slots,
        "tray_status": tray_status,
        "annotated_image_base64": encoded_image
    }
