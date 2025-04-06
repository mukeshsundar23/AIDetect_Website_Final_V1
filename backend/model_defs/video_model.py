import torch
import numpy as np
import cv2
import os
import tempfile
import base64
from io import BytesIO
from PIL import Image
from backend.model_defs.model import DeepfakeDetectionModel


# Load model
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "video", "ResNext + LSTM.pt")
)

model = DeepfakeDetectionModel()
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")), strict=False)
model.eval()

def extract_frames(video_path, num_frames=16):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_idxs = np.linspace(0, total_frames - 1, num_frames, dtype=np.int32)

    frames = []
    raw_images = []  # Store raw images as numpy arrays directly
    
    for idx in frame_idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # Store the raw frame before normalization
            raw_frame = cv2.resize(frame, (224, 224))
            raw_frame_rgb = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)
            raw_images.append(raw_frame_rgb)
            
            # Process frame for model input
            frame = cv2.resize(frame, (224, 224))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
    cap.release()

    if len(frames) != num_frames:
        raise ValueError("Not enough frames extracted.")

    # Process frames for model input
    frames = np.stack(frames).astype(np.float32) / 255.0
    frames = torch.tensor(frames).permute(0, 3, 1, 2)  # (T, C, H, W)
    
    return [f.unsqueeze(0).unsqueeze(0) for f in frames], raw_images  # list of (1, 1, C, H, W), list of numpy arrays

async def predict_video(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            temp.write(await file.read())
            temp_path = temp.name

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        video_frames, raw_images = extract_frames(temp_path)
        frame_predictions = []

        with torch.no_grad():
            for idx, (frame_tensor, raw_img) in enumerate(zip(video_frames, raw_images)):
                # Get model prediction
                output = model(frame_tensor)
                # Extract probability - fix tensor conversion issue
                prob = output.item() if output.numel() == 1 else output[0][0].item()
                label = "Fake" if prob > 0.5 else "Real"
                confidence = float(prob if label == "Fake" else 1 - prob)

                # Process image for display - raw_img is already a numpy array
                img_cv = cv2.cvtColor(raw_img, cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                try:
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)
                except Exception:
                    # If face detection fails, continue without drawing boxes
                    pass

                # Convert to base64 for frontend
                boxed_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(boxed_img)
                buffered = BytesIO()
                pil_img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                img_data_uri = f"data:image/jpeg;base64,{img_str}"

                # Add to predictions
                frame_predictions.append({
                    "frame": idx + 1,
                    "label": label,
                    "confidence": float(round(confidence, 4)),  # Ensure it's a float, not tensor
                    "thumbnail": img_data_uri
                })

        # Handle empty predictions
        if not frame_predictions:
            return {
                "frame_predictions": [],
                "final": {
                    "label": "Unknown",
                    "confidence": 0.0
                }
            }

        # Calculate final prediction
        labels = [fp["label"] for fp in frame_predictions]
        final_label = max(set(labels), key=labels.count) if labels else "Unknown"
        final_confidences = [fp["confidence"] for fp in frame_predictions if fp["label"] == final_label]
        avg_confidence = sum(final_confidences) / len(final_confidences) if final_confidences else 0.0

        # Clean up
        os.remove(temp_path)

        # Return results
        return {
            "frame_predictions": frame_predictions,
            "final": {
                "label": final_label,
                "confidence": float(round(avg_confidence, 4))  # Ensure it's a float
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        return {"error": str(e)}