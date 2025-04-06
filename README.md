# AI-Generated Content Detection Platform

A full-stack, multimodal content analysis platform that detects AI-generated text, images (including deepfakes), and videos. Built using **FastAPI**, **deep learning models**, and a **Jinja2-based frontend**, this project brings together cutting-edge AI detection into a unified web application.

---

## 🚀 Features

- 📝 **Text Detection**: Detect AI-generated content (e.g., ChatGPT essays) using a Transformer based classifier.
- 🖼️ **Image Deepfake Detection**: Analyze images for signs of manipulation or generation using RNN + LSTM models.
- 🎥 **Video Deepfake Detection**: Frame-by-frame facial analysis using RNN + LSTM models.
- 🌐 **Unified Frontend**: Jinja2-rendered HTML templates with clear navigation and result display.
- 🐳 **Dockerized**: Fully containerized for quick deployment (e.g., Render, AWS, Azure).

---

## 📂 Project Structure

```
.
├── api.py
├── backend/
│   ├── model_defs/
│   │   ├── text_model.py
│   │   ├── image_model.py
│   │   └── video_model.py
│   └── models/
│       ├── text/
│       │   ├── ai_text_model/
│       │   └── vectorizer_model/
│       ├── image/
│       └── video/
│           └── ResNext + LSTM.pt
├── frontend/
│   ├── scripts/
│   │   └── script.js
│   ├── styles/
│   └── templates/
│       ├── index.html
│       ├── text-detection.html
│       ├── image-detection.html
│       ├── video-detection.html
│       └── 404.html
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🧪 Local Development

### 1. Clone the repository

```bash
git clone https://github.com/mukeshsundar23/AIDetect_Website_V1.git
cd AIDetect_Website_V1
```

### 2. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the app

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Visit [http://localhost:8000](http://localhost:8000) to access the web interface.

---

## 🐳 Docker Deployment

### Build and run locally:

```bash
docker build -t ai-detect-platform .
docker run -d -p 8000:8000 ai-detect-platform
```

### Push to Docker Hub

```bash
docker tag ai-detect-platform mukesh2306/aidetect_website_final_v1-server:latest
docker push mukesh2306/aidetect_website_final_v1-server:latest
```

---

## ☁️ Deploy to Render

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **New → Web Service → Deploy an existing image from registry**
3. Image: `mukesh2306/aidetect_website_final_v1-server:latest`
4. Port: `8000`

Your app will be live at:  
```
https://<your-app-name>.onrender.com
```

---

## 📦 Tech Stack

- **FastAPI**
- **PyTorch, Transformers**
- **dlib, OpenCV**
- **Uvicorn**
- **Jinja2 Templates**
- **Docker**

---

## 📃 License

This project is licensed under the MIT License. See the [`LICENSE`](./LICENSE) file for details.

---

## 👨‍💻 Author

**Mukesh Sundar P**  
Final Year Project | Multimodal AI Content Detection  
GitHub: [@mukeshsundar23](https://github.com/mukeshsundar23)

---

## 🙌 Contributions & Feedback

Pull requests and feedback are welcome. Open an issue for bugs, improvements, or questions.

