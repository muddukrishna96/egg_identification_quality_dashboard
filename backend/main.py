from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from backend.yolo_inference  import process_egg_tray

app = FastAPI()

# Allow CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # Read file bytes
    image_bytes = await file.read()

    # Run backend logic
    result = process_egg_tray(image_bytes)

    # Return JSON with metrics and base64 image
    return result
