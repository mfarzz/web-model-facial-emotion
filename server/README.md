# Neo Telemetri Facial Emotion Recognition Server

Server-side implementation untuk deteksi emosi wajah menggunakan Deep Learning dengan kemampuan penanganan background noise yang advanced.

## 🎯 Fitur Utama

- **Advanced Noise Reduction**: Mengurangi noise dari background untuk deteksi wajah yang lebih akurat
- **Multi-scale Face Detection**: Deteksi wajah dengan berbagai ukuran menggunakan Haarcascade
- **False Positive Filtering**: Filter otomatis untuk menghilangkan deteksi wajah palsu
- **Real-time Processing**: Pemrosesan real-time untuk aplikasi web
- **Robust Preprocessing**: Pipeline preprocessing yang kuat untuk berbagai kondisi pencahayaan

## 🏗️ Arsitektur

```
Input Image → Noise Reduction → Face Detection → Face Extraction → Emotion Prediction → JSON Response
```

### Pipeline Detail:
1. **Image Preprocessing**: Noise reduction, contrast enhancement, illumination correction
2. **Face Detection**: Multi-scale Haarcascade detection dengan parameter adaptif
3. **False Positive Filtering**: Filter berdasarkan aspect ratio, ukuran, dan variance
4. **Face ROI Extraction**: Ekstraksi region of interest dengan padding optimal
5. **Emotion Classification**: Prediksi menggunakan DCNN model (happy, sad, neutral)

## 📦 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd web-model-facial-emotion/server
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit .env file sesuai konfigurasi Anda
# nano .env  # atau gunakan text editor favorit
```

### 4. Verifikasi File Model
Pastikan file-file berikut ada:
- `../model/model.h5` - Model emotion recognition yang sudah dilatih
- `../model/haarcascade_frontalface_default.xml` - Haarcascade classifier

Atau jika menggunakan folder `assets/`:
- `assets/model.h5`
- `assets/haarcascade_frontalface_default.xml`

## ⚙️ Konfigurasi Environment

File `.env` berisi konfigurasi penting untuk server:

```bash
# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True

# Server Configuration  
HOST=127.0.0.1
PORT=5000

# Model Paths
MODEL_PATH=assets/model.h5
CASCADE_PATH=assets/haarcascade_frontalface_default.xml

# Image Processing
MAX_IMAGE_SIZE=2048
CONFIDENCE_THRESHOLD=0.7

# Face Detection Parameters
SCALE_FACTOR=1.1
MIN_NEIGHBORS=5
```

**Catatan**: Jangan commit file `.env` ke repository untuk keamanan!

## 🚀 Menjalankan Server

### Development Mode
```bash
python run_server.py --debug
```

### Production Mode
```bash
python run_server.py --host 0.0.0.0 --port 5000
```

### Custom Configuration
```bash
python run_server.py --model-path /path/to/model.h5 --cascade-path /path/to/haarcascade.xml
```

## 📡 API Endpoints

### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-08-09T12:00:00"
}
```

### 2. Predict from Base64 Image
```
POST /predict
Content-Type: application/json
```

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Response:**
```json
{
  "success": true,
  "faces_count": 1,
  "faces": [
    {
      "face_id": 1,
      "emotion": "happy",
      "confidence": 85.67,
      "coordinates": {
        "x": 150,
        "y": 80,
        "width": 120,
        "height": 140
      },
      "all_probabilities": {
        "happy": 85.67,
        "sad": 8.21,
        "neutral": 6.12
      },
      "quality_metrics": {
        "face_area_percentage": 15.23,
        "aspect_ratio": 0.86
      }
    }
  ],
  "message": "Successfully detected and analyzed 1 face(s) with noise-resistant processing",
  "processing_info": {
    "noise_reduction_applied": true,
    "multi_scale_detection": true,
    "false_positive_filtering": true
  }
}
```

### 3. Predict from File Upload
```
POST /predict_file
Content-Type: multipart/form-data
```

**Request:**
```
file: <image_file>
```

## 🧪 Testing

### 1. Menggunakan Test Script
```bash
python test_api.py
```

### 2. Manual Testing dengan cURL
```bash
# Health check
curl -X GET http://localhost:5000/health

# Predict from file
curl -X POST -F "file=@test_image.jpg" http://localhost:5000/predict_file
```

### 3. Testing dengan Noisy Background
Script test_api.py menyediakan fungsi untuk testing dengan background noise artifisial.

## 🔧 Konfigurasi Advanced

### Environment Variables
```bash
export MODEL_PATH="/path/to/model.h5"
export CASCADE_PATH="/path/to/haarcascade.xml"
export FLASK_DEBUG="true"
export HOST="0.0.0.0"
export PORT="5000"
```

### Parameter Tuning
Edit `config.py` untuk menyesuaikan:
- Face detection parameters
- Noise reduction settings
- Image processing configurations

## 🎨 Integrasi dengan Frontend

### JavaScript Example
```javascript
// Fungsi untuk mengirim gambar ke server
async function predictEmotion(imageBase64) {
    const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: imageBase64
        })
    });
    
    return await response.json();
}

// Menggunakan dengan webcam
async function predictFromWebcam() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    const imageBase64 = canvas.toDataURL('image/jpeg');
    const result = await predictEmotion(imageBase64);
    
    console.log('Emotion prediction:', result);
}
```

## 🔒 Keamanan

- Input validation untuk image format
- Size limiting untuk upload file
- Rate limiting (bisa ditambahkan dengan Flask-Limiter)
- CORS configuration untuk web integration

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Production Recommendations
- Gunakan Gunicorn atau uWSGI
- Setup reverse proxy dengan Nginx
- Implementasi logging yang proper
- Monitoring dan alerting
- Load balancing untuk high traffic

## 🐛 Troubleshooting

### Common Issues

1. **Model tidak ditemukan**
   ```
   Error: Model file not found
   ```
   **Solution**: Pastikan file `model.h5` ada di path yang benar

2. **Haarcascade tidak ditemukan**
   ```
   Error: Could not load cascade classifier
   ```
   **Solution**: Download haarcascade_frontalface_default.xml dari OpenCV

3. **TensorFlow/CUDA Issues**
   ```
   Could not load dynamic library 'cudart64_110.dll'
   ```
   **Solution**: Install TensorFlow CPU version atau setup CUDA properly

4. **Memory Issues**
   ```
   Out of memory error
   ```
   **Solution**: Reduce batch size atau optimize image size

## 📊 Performance

### Benchmarks
- **Face Detection**: ~50ms per image (CPU)
- **Emotion Prediction**: ~30ms per face (CPU)
- **Total Processing**: ~100ms per image dengan 1 wajah
- **Memory Usage**: ~500MB (model loaded)

### Optimization Tips
- Resize image sebelum processing
- Batch processing untuk multiple images
- Caching untuk model inference
- Asynchronous processing untuk high load

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add tests untuk fitur baru
4. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

Untuk support dan pertanyaan:
- Email: support@neotelemetri.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues]
