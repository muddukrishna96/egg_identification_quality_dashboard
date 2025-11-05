# backend/test_inference.py

import base64
import cv2
import numpy as np
from yolo_inference import process_egg_tray

def test_backend_inference(image_path: str):
    """
    Test function to run YOLO egg tray detection backend independently.
    It reads an image, passes it to process_egg_tray, and displays the result.
    """

    # Read image and convert to bytes (simulate frontend upload)
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Run inference
    print("🔍 Running backend inference...")
    result = process_egg_tray(image_bytes)

    # Decode base64 image back to OpenCV format
    image_data = base64.b64decode(result["annotated_image_base64"])
    image_np = np.frombuffer(image_data, np.uint8)
    output_img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # Save result image locally for inspection
    output_path = "backend/test_output.jpg"
    cv2.imwrite(output_path, output_img)

    # Print results
    print("\n===== Inference Results =====")
    print(f"Tray Status     : {result['tray_status']}")
    print(f"Eggs Detected   : {result['num_eggs']}")
    print(f"Empty Slots     : {result['num_empty_slots']}")
    print(f"Output Image    : {output_path}")
    print("=============================\n")

    # Optionally display image in a window
    cv2.imshow("Annotated Output", output_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # 🔸 Change this path to one of your local test images
    test_image_path = r"C:\Users\muddu krishna\Desktop\personal\projects personal\egg_identification_quality_dashboard\src\egg_identification-2\test\images\IMG_6524_MOV-0079_jpg.rf.32236270917cb39dae0dfbbf13361e03.jpg"
    test_backend_inference(test_image_path)
