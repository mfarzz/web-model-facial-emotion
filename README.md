# 🎭 Web-based Facial Emotion Recognition

**Real-time facial emotion detection menggunakan Deep Learning dan Computer Vision**

<div align="center">

![Emotion Detection Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow)
![Flask](https://img.shields.io/badge/Flask-2.x-red)

</div>

## 📋 Deskripsi

Sistem deteksi emosi wajah real-time yang menggunakan Deep Convolutional Neural Network (DCNN) untuk mengklasifikasikan emosi manusia menjadi 3 kategori: **Senang**, **Sedih**, dan **Netral**. Aplikasi ini terdiri dari frontend web modern dan backend Flask API yang dioptimasi untuk performa tinggi.

## ✨ Fitur Utama

### 🎯 **Deteksi Real-time**
- Deteksi emosi real-time dengan kamera web
- Frame rate optimal: 3-5 FPS untuk performa terbaik
- Multi-face detection dengan bounding box tracking
- Adaptive performance optimization

### 🧠 **AI/ML Engine**
- Model DCNN 3-class emotion classification
- OpenCV Haarcascade face detection
- Confidence scoring dan akurasi tracking
- Noise reduction dan image preprocessing

### 🎨 **User Interface**
- Modern responsive web design
- Real-time face tracking dengan colored boxes
- Emotion history dan statistics dashboard
- Multi-camera support dengan switcher
- Smooth animations dan transitions

### ⚡ **Performance Optimization**
- Image compression dan resolution scaling
- Request debouncing dan frame skipping
- Adaptive detection rate berdasarkan performance
- Optimized server-side processing

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   Frontend      │◄──────────────►│   Backend       │
│   (Web Client)  │                 │   (Flask API)   │
├─────────────────┤                 ├─────────────────┤
│ • HTML5/CSS3    │                 │ • Flask Server  │
│ • JavaScript    │                 │ • TensorFlow    │
│ • WebRTC API    │                 │ • OpenCV        │
│ • Canvas 2D     │                 │ • NumPy         │
│ • Real-time UI  │                 │ • PIL/Pillow    │
└─────────────────┘                 └─────────────────┘
```

## 📁 Struktur Project

```
web-model-facial-emotion/
│
├── 📁 web/                     # Frontend Application
│   ├── index.html              # Main HTML file
│   ├── script.js               # Core JavaScript logic
│   ├── style.css               # Responsive styling
│   └── assets/                 # Static assets
│       ├── Logo Neo.svg
│       ├── left.svg
│       └── right.svg
│
├── 📁 server/                  # Backend API
│   ├── app.py                  # Flask server main
│   ├── image_utils.py          # Image processing utilities
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   └── README.md               # Server documentation
│
├── 📁 model/                   # AI Model & Training
│   ├── facial-emotion-recognition.ipynb
│   ├── epoch_history_dcnn.png
│   └── performance_dist.png
│
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. **Setup Backend**

```bash
# Navigate to server directory
cd server

# Install Python dependencies
pip install -r requirements.txt

# Start Flask server
python app.py
```

Server akan berjalan di: `http://127.0.0.1:5000`

### 2. **Setup Frontend**

```bash
# Navigate to web directory
cd web

# Start local server (pilih salah satu)
python -m http.server 8000        # Python
# atau
npx serve .                       # Node.js
# atau buka langsung index.html di browser
```

Frontend akan berjalan di: `http://localhost:8000`

### 3. **Akses Aplikasi**

1. Buka browser dan navigasi ke frontend URL
2. Izinkan akses kamera ketika diminta
3. Klik "**Mulai Deteksi**" untuk memulai
4. Lihat emosi terdeteksi secara real-time!

## 🛠️ Instalasi Detail

### **Prerequisites**

- Python 3.8 atau lebih tinggi
- Webcam/Camera device
- Browser modern (Chrome, Firefox, Safari, Edge)

### **Backend Dependencies**

```bash
pip install flask
pip install tensorflow
pip install opencv-python
pip install numpy
pip install pillow
pip install flask-cors
```

### **Model Requirements**

Model DCNN harus ditempatkan di `server/models/`:
- `emotion_model.h5` - Trained model file
- `haarcascade_frontalface_default.xml` - Face detection cascade

## 🎛️ Konfigurasi

### **Server Configuration** (`server/config.py`)

```python
# Server settings
HOST = '127.0.0.1'
PORT = 5000
DEBUG = True

# Model settings
CONFIDENCE_THRESHOLD = 0.6
MAX_FACES_PER_IMAGE = 3

# Performance settings
ENABLE_GAUSSIAN_BLUR = True
FACE_DETECTION_MIN_SIZE = (30, 30)
```

### **Frontend Configuration** (`web/script.js`)

```javascript
// Detection settings
detectionInterval: 300,        // 300ms = ~3.3 FPS
maxSkipFrames: 2,             // Frame skipping
imageQuality: 0.6,            // JPEG compression
maxResolution: 320x240,       // Processing resolution
```

## 📊 Performance Metrics

### **Timing Benchmarks**
- **Total Detection Time**: 80-220ms
- **Server Processing**: 60-180ms
- **Network Latency**: 10-50ms
- **Frame Rate**: 3-5 FPS optimal

### **Accuracy Metrics**
- **Model Accuracy**: ~85-90% pada test set
- **Real-time Confidence**: 60-95% threshold
- **Face Detection Rate**: >95% untuk wajah frontal

## 🎯 Penggunaan

### **Basic Usage**

1. **Start Detection**: Klik tombol "Mulai Deteksi"
2. **Camera Selection**: Pilih kamera jika tersedia multiple
3. **View Results**: Lihat emosi real-time dengan bounding box
4. **History**: Check riwayat deteksi di panel samping
5. **Statistics**: Monitor akurasi dan statistik deteksi

### **Advanced Features**

- **Multi-face Detection**: Sistem dapat mendeteksi multiple wajah
- **Adaptive Performance**: Frame rate menyesuaikan dengan kecepatan sistem
- **Camera Switching**: Ganti kamera tanpa restart aplikasi
- **Real-time Statistics**: Monitor performa dan akurasi live

## 🔧 Troubleshooting

### **Common Issues**

**❌ Camera Permission Denied**
```
Solution: Enable camera permission di browser settings
Chrome: Settings > Privacy > Camera > Allow
```

**❌ Server Connection Failed**
```
Solution: Pastikan Flask server berjalan di port 5000
Check: http://127.0.0.1:5000/health
```

**❌ Model Not Found**
```
Solution: Download dan letakkan model di server/models/
Required: emotion_model.h5, haarcascade_frontalface_default.xml
```

**❌ Slow Performance**
```
Solution: 
- Reduce camera resolution
- Close unnecessary applications
- Check CPU/memory usage
```

## 📈 Development

### **Development Setup**

```bash
# Clone repository
git clone [repository-url]
cd web-model-facial-emotion

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r server/requirements.txt

# Development mode
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python server/app.py
```

### **Code Structure**

**Frontend (JavaScript)**
- `EmotionDetector` class: Core detection logic
- Real-time video processing dengan Canvas API
- WebRTC camera integration
- Performance monitoring dan optimization

**Backend (Python)**
- `EmotionPredictor` class: Model inference
- Flask API endpoints untuk prediction
- Image preprocessing dengan OpenCV
- Error handling dan logging

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 API Documentation

### **Endpoints**

**Health Check**
```http
GET /health
Response: {"status": "healthy", "timestamp": "..."}
```

**Emotion Prediction**
```http
POST /predict
Content-Type: application/json

Request Body:
{
  "image": "data:image/jpeg;base64,..."
}

Response:
{
  "success": true,
  "faces_detected": 1,
  "emotions": [
    {
      "emotion": "happy",
      "confidence": 0.85,
      "bounding_box": {
        "x": 120, "y": 80,
        "width": 150, "height": 180
      }
    }
  ],
  "processing_time": 95.23
}
```

## 🔄 Version History

- **v1.0.0** - Initial release dengan basic emotion detection
- **v1.1.0** - Added multi-face detection dan performance optimization
- **v1.2.0** - Real-time face tracking dengan bounding boxes
- **v1.3.0** - Adaptive performance dan comprehensive optimization

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**Neo Telemetri Development Team**
- Lead Developer: [Your Name]
- AI/ML Engineer: [Team Member]
- Frontend Developer: [Team Member]

## 🙏 Acknowledgments

- TensorFlow team untuk machine learning framework
- OpenCV community untuk computer vision tools
- Flask developers untuk web framework
- Contributors dan testers

---

<div align="center">

**🎭 Built with ❤️ by Neo Telemetri Team**

[📧 Contact](mailto:contact@neotelemetri.com) • [🌐 Website](https://neotelemetri.com) • [📱 Demo](demo-link)

</div>
