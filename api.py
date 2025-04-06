from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# Import model-specific logic
from backend.model_defs.text_model import predict_text
from backend.model_defs.video_model import predict_video
# from model_defs.image_model import predict_image  # optional for later

app = FastAPI(
    title="Multimodal AI Content Detection API",
    description="Detects AI-generated content in text, images, and video",
    version="1.0.0"
)

# Serve static files and Jinja2 templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")), name="static")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5500"] for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------- TEXT DETECTION -----------
class TextInput(BaseModel):
    text: str

class TextDetectionRequest(BaseModel):
    text: str
    explain: bool = False

@app.post("/predict")
def text_detection(input_data: TextInput):
    """
    Detect if the input text is AI-generated or human-written.
    """
    return predict_text(input_data.text)

@app.post("/text-detect")
async def detect_text(request: TextDetectionRequest):
    """
    Detect if the input text is AI-generated or human-written with optional explanations.
    """
    try:
        result = predict_text(request.text, explain=request.explain)
        return result
    except Exception as e:
        return {"error": str(e)}


# ----------- VIDEO DETECTION -----------
@app.post("/video-detect")
async def video_detection(file: UploadFile = File(...)):
    """
    Detect if a video contains deepfake content.
    """
    return await predict_video(file)


# ----------- IMAGE DETECTION (Optional) -----------
# Import the image model
from backend.model_defs.image_model import predict_image

# Update the image detection endpoint
@app.post("/image-detect")
async def image_detection(file: UploadFile = File(...)):
    """
    Detect if an image is AI-generated using the video model.
    """
    return await predict_image(file)

# Serve frontend pages
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/text", response_class=HTMLResponse)
async def text_page(request: Request):
    return templates.TemplateResponse("text-detection.html", {"request": request})

@app.get("/image", response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse("image-detection.html", {"request": request})

@app.get("/video", response_class=HTMLResponse)
async def video_page(request: Request):
    return templates.TemplateResponse("video-detection.html", {"request": request})