import torch
import numpy as np
import cv2
import os
import base64
from io import BytesIO
from PIL import Image
from backend.model_defs.model import DeepfakeDetectionModel

# Use the same model as video detection
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "video", "ResNext + LSTM.pt")
)

# Load the model once
model = DeepfakeDetectionModel()
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")), strict=False)
model.eval()

async def predict_image(file):
    """Predict if an image is AI-generated using the video deepfake model"""
    try:
        # Read the image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"error": "Could not read image file"}
        
        # Resize and preprocess the image
        img_resized = cv2.resize(img, (224, 224))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        # Store the raw image for visualization
        raw_img = img_rgb.copy()
        
        # Normalize and convert to tensor
        img_tensor = torch.tensor(img_rgb.astype(np.float32) / 255.0)
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0).unsqueeze(0)  # (1, 1, C, H, W)
        
        # Face detection for visualization
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        
        try:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
        except Exception:
            # If face detection fails, continue without drawing boxes
            pass
        
        # Get model prediction
        with torch.no_grad():
            output = model(img_tensor)
            prob = output.item() if output.numel() == 1 else output[0][0].item()
            
        # Determine label and confidence
        label = "AI-generated" if prob > 0.5 else "Real"
        confidence = float(prob if label == "AI-generated" else 1 - prob)
        
        # Generate heatmap for explainability
        # This is a simplified version - for true LIME you'd need more complex implementation
        heatmap = generate_simple_heatmap(img_rgb, model)
        
        # Convert images to base64 for frontend
        boxed_img = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(boxed_img)
        buffered = BytesIO()
        pil_img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Convert heatmap to base64
        heatmap_pil = Image.fromarray(heatmap)
        heatmap_buffered = BytesIO()
        heatmap_pil.save(heatmap_buffered, format="JPEG")
        heatmap_str = base64.b64encode(heatmap_buffered.getvalue()).decode("utf-8")
        
        # Generate explanations
        lime_explanations = generate_explanations(label, confidence, faces)
        
        return {
            "label": label,
            "confidence": round(confidence, 4),
            "image": f"data:image/jpeg;base64,{img_str}",
            "heatmap_image": f"data:image/jpeg;base64,{heatmap_str}",
            "lime_explanations": lime_explanations
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def generate_simple_heatmap(img, model):
    """Generate a simple heatmap for explainability"""
    # Create a heatmap by analyzing different regions of the image
    # This is a simplified approach - not true LIME but gives visual explanation
    
    height, width = img.shape[:2]
    heatmap = np.zeros((height, width), dtype=np.float32)
    
    # Create a grid of patches
    patch_size = 56  # 4x4 grid on 224x224 image
    
    for y in range(0, height, patch_size):
        for x in range(0, width, patch_size):
            # Create a masked version of the image with this patch visible
            masked_img = np.zeros_like(img)
            y_end = min(y + patch_size, height)
            x_end = min(x + patch_size, width)
            
            masked_img[y:y_end, x:x_end] = img[y:y_end, x:x_end]
            
            # Get prediction for this masked image
            masked_tensor = torch.tensor(masked_img.astype(np.float32) / 255.0)
            masked_tensor = masked_tensor.permute(2, 0, 1).unsqueeze(0).unsqueeze(0)
            
            with torch.no_grad():
                output = model(masked_tensor)
                prob = output.item() if output.numel() == 1 else output[0][0].item()
            
            # Fill the heatmap region with the probability
            heatmap[y:y_end, x:x_end] = prob
    
    # Normalize and colorize the heatmap
    heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap = heatmap.astype(np.uint8)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    
    # Blend with original image
    original_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    blended = cv2.addWeighted(original_img, 0.7, heatmap, 0.3, 0)
    blended_rgb = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
    
    return blended_rgb

def generate_explanations(label, confidence, faces):
    """Generate human-readable explanations based on the model's prediction"""
    explanations = []
    
    # Add overall explanation
    explanations.append(f"Model detected {label} image with {round(confidence*100)}% confidence")
    
    # Add face-related explanations
    if len(faces) > 0:
        explanations.append(f"Detected {len(faces)} face(s) in the image")
        if label == "AI-generated":
            explanations.append("Check facial features for unnatural smoothness or asymmetry")
            explanations.append("Examine eye details, reflections, and pupil shapes")
        else:
            explanations.append("Facial features appear natural and consistent")
    else:
        if label == "AI-generated":
            explanations.append("No faces detected - examine overall image consistency")
        else:
            explanations.append("No faces detected - image appears to have natural patterns")
    
    # Add general explanations based on confidence
    if label == "AI-generated":
        if confidence > 0.8:
            explanations.append("High confidence in AI generation detection")
            explanations.append("Check for unnatural textures and inconsistent lighting")
        else:
            explanations.append("Moderate confidence in AI generation detection")
            explanations.append("Some AI artifacts may be present but subtle")
    else:
        if confidence > 0.8:
            explanations.append("High confidence this is an authentic image")
            explanations.append("Natural patterns and consistent details throughout")
        else:
            explanations.append("Moderate confidence this is an authentic image")
            explanations.append("Some areas may have unusual patterns but likely natural")
    
    return explanations