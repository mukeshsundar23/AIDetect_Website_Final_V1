# AI Content Detection Backend

This repository contains the backend service for a multi-modal AI-generated content detection system. It supports detecting AI-generated content across:

- 📝 Text (e.g., ChatGPT-generated essays)
- 🖼️ Images (e.g., deepfakes or AI-generated photos)
- 🎥 Videos (e.g., deepfake videos)

The backend is built using **FastAPI** and is packaged in a lightweight, production-ready **Docker container** for easy deployment.

---

## 🚀 Features

- 🔍 **Text Detection**: Uses a fine-tuned RoBERTa model to classify content as human-written or AI-generated.
- 🧠 **Image & Video Deepfake Detection**: Frame-by-frame facial analysis using CNN + LSTM for deepfake detection.
- 🐳 **Dockerized**: Fully containerized and ready to deploy on platforms like Render, Azure, or any Docker host.
- 🌐 **REST API**: Clean, documented endpoints via FastAPI.

---

## 📂 Project Structure

```
.
├── api.py                # FastAPI main app
├── model_defs/           # Contains model classes and load logic
│   ├── text_model.py
│   ├── image_model.py
│   └── video_model.py
├── models/               # Contains model weights
│   ├── roberta-sentinel.pth
│   └── ResNext+LSTM.pt
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🧪 Local Development

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-detector-backend.git
cd ai-detector-backend
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the API

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Access it at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Run with Docker

### 1. Build the image

```bash
docker build -t aidetect_backend .
```

### 2. Run the container

```bash
docker run -d -p 8000:8000 aidetect_backend
```

---

## ☁️ Deploy to Render

1. Push your Docker image to Docker Hub:

```bash
docker tag aidetect_backend mukesh2306/aidetect_website_final_v1-server:latest
docker push mukesh2306/aidetect_website_final_v1-server:latest
```

2. Go to [https://dashboard.render.com](https://dashboard.render.com)
3. Click **New → Web Service → Deploy an existing image from a registry**
4. Enter:

```
Image: mukesh2306/aidetect_website_final_v1-server:latest
Port: 8000
```

5. Done! Your API is live at:

```
https://<your-app-name>.onrender.com
```

---

## 🛠 API Endpoints (Sample)

| Endpoint            | Method | Description                      |
|---------------------|--------|----------------------------------|
| `/detect/text`      | POST   | Detect if a text is AI-generated |
| `/detect/image`     | POST   | Detect if an image is fake       |
| `/detect/video`     | POST   | Detect deepfake in video         |

---

## 📦 Dependencies

- `FastAPI`
- `Uvicorn`
- `transformers`
- `torch`
- `opencv-python`
- `dlib`, `face-recognition-models` (for video deepfake)
- `pydantic`, `scikit-learn`

---

## 📃 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## 👨‍💻 Author

**Sriram S Seenivasan**

- GitHub: [@SriramS-Dev](https://github.com/SriramS-Dev)
- Project Lead for AI-generated Content Detection Final Year Project

---

## 🗣️ Feedback & Contributions

Feel free to open issues or submit PRs for improvements. Collaboration is welcome!
