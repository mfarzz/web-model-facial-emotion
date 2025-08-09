// Neo Telemetri - Facial Emotion Recognition
class EmotionDetector {
    constructor() {
        this.video = document.getElementById('videoElement');
        this.canvas = this.createCanvas();
        this.ctx = this.canvas.getContext('2d');
        
        this.isDetecting = false;
        this.detectionInterval = null;
        this.stream = null;
        this.lastDetectionTime = 0;
        this.hideBoxTimeout = null;
        
        // Face tracking
        this.currentFaces = [];
        this.lastSuccessfulDetection = 0;
        this.faceBoxVisible = false;
        
        // Performance optimization
        this.pendingRequest = false;
        this.skipFrames = 0;
        this.maxSkipFrames = 2; // Skip 2 frames between detections untuk speed
        this.adaptiveRate = true;
        this.slowDetectionCount = 0;
        
        this.stats = {
            totalDetections: 0,
            facesDetected: 0,
            accuracySum: 0
        };
        
        this.emotionMap = {
            'happy': { icon: '😊', color: '#FFD700' },
            'sad': { icon: '😢', color: '#4169E1' },
            'neutral': { icon: '😐', color: '#808080' }
        };
        
        this.serverUrl = 'http://127.0.0.1:5000';
        
        // Camera settings
        this.availableCameras = [];
        this.selectedCameraId = null;
        
        this.initializeUI();
        this.initializeEventListeners();
        this.getCameraList().then(() => {
            this.requestCameraPermission();
        });
    }
    
    createCanvas() {
        const canvas = document.createElement('canvas');
        canvas.style.display = 'none';
        document.body.appendChild(canvas);
        return canvas;
    }
    
    initializeUI() {
        // Create camera status display
        const cameraContainer = document.querySelector('.camera-container');
        if (cameraContainer && !document.querySelector('.camera-status')) {
            const statusDiv = document.createElement('div');
            statusDiv.className = 'camera-status';
            statusDiv.innerHTML = `
                <div class="status-icon">📷</div>
                <span>Meminta izin kamera...</span>
            `;
            cameraContainer.appendChild(statusDiv);
        }
        
        // Create controls
        const controlsDiv = document.querySelector('.controls');
        if (controlsDiv && !document.querySelector('#startBtn')) {
            controlsDiv.innerHTML = `
                <button id="startBtn" class="btn btn-primary">
                    <i>▶️</i> Mulai Deteksi
                </button>
                <button id="stopBtn" class="btn btn-secondary" disabled>
                    <i>⏹️</i> Berhenti
                </button>
            `;
        }
        
        // Create emotion result display
        const emotionResult = document.querySelector('.emotion-result');
        if (emotionResult && !document.querySelector('.emotion-display')) {
            emotionResult.innerHTML = `
                <div class="emotion-display">
                    <div class="emotion-icon">😐</div>
                    <div class="emotion-text">Menunggu deteksi...</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: 0%"></div>
                    </div>
                    <div class="confidence-text">Akurasi: 0%</div>
                </div>
                
                <div class="history-section">
                    <h4>Riwayat Deteksi</h4>
                    <div class="history-list" id="historyList">
                        <div class="history-empty">Belum ada deteksi</div>
                    </div>
                </div>
            `;
        }
        
        // Create stats display
        const statsDiv = document.querySelector('.detection-stats');
        if (statsDiv && !document.querySelector('.stats-grid')) {
            statsDiv.innerHTML = `
                <h4>Statistik</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">Total Deteksi</div>
                        <div class="stat-value" id="totalDetections">0</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Wajah Terdeteksi</div>
                        <div class="stat-value" id="facesDetected">0</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Akurasi Rata-rata</div>
                        <div class="stat-value" id="avgAccuracy">0%</div>
                    </div>
                </div>
            `;
        }
        
        // Get UI elements
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.cameraStatus = document.querySelector('.camera-status');
        this.emotionDisplay = document.querySelector('.emotion-display');
        this.historyList = document.getElementById('historyList');
        this.faceOverlay = document.querySelector('.face-overlay');
    }
    
    initializeEventListeners() {
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => this.startDetection());
        }
        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stopDetection());
        }
        
        window.addEventListener('resize', () => this.adjustVideoSize());
    }
    
    async getCameraList() {
        try {
            // Get list of available cameras
            const devices = await navigator.mediaDevices.enumerateDevices();
            this.availableCameras = devices.filter(device => device.kind === 'videoinput');
            
            console.log('Available cameras:', this.availableCameras);
            
            // Add camera selector to UI if multiple cameras available
            if (this.availableCameras.length > 1) {
                this.addCameraSelector();
            }
            
        } catch (error) {
            console.error('Error getting camera list:', error);
        }
    }
    
    addCameraSelector() {
        const cameraContainer = document.querySelector('.camera-container');
        if (cameraContainer && !document.querySelector('#cameraSelector')) {
            const selectorDiv = document.createElement('div');
            selectorDiv.className = 'camera-selector';
            
            let optionsHtml = '<option value="">Pilih Kamera</option>';
            this.availableCameras.forEach((camera, index) => {
                const label = camera.label || `Kamera ${index + 1}`;
                optionsHtml += `<option value="${camera.deviceId}">${label}</option>`;
            });
            
            selectorDiv.innerHTML = `
                <label for="cameraSelector">Kamera:</label>
                <select id="cameraSelector" class="camera-select">
                    ${optionsHtml}
                </select>
            `;
            
            // Insert before video element
            cameraContainer.insertBefore(selectorDiv, cameraContainer.firstChild);
            
            // Add event listener for camera change
            document.getElementById('cameraSelector').addEventListener('change', (e) => {
                this.selectedCameraId = e.target.value;
                if (this.selectedCameraId) {
                    this.switchCamera(this.selectedCameraId);
                }
            });
        }
    }
    
    async switchCamera(deviceId) {
        try {
            // Stop current stream
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }
            
            this.updateStatus('🔄', 'Mengganti kamera...');
            
            // Request new camera
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    deviceId: deviceId ? { exact: deviceId } : undefined,
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            });
            
            // Setup new video stream
            this.video.srcObject = stream;
            this.stream = stream;
            
            this.video.onloadedmetadata = () => {
                this.canvas.width = this.video.videoWidth;
                this.canvas.height = this.video.videoHeight;
                this.adjustVideoSize();
                this.updateStatus('✅', 'Kamera berhasil diganti');
            };
            
        } catch (error) {
            console.error('Error switching camera:', error);
            this.updateStatus('❌', 'Gagal mengganti kamera');
        }
    }
    
    async requestCameraPermission() {
        try {
            this.updateStatus('🔄', 'Meminta izin kamera...');
            
            // Prepare camera constraints
            const videoConstraints = {
                width: { ideal: 640 },
                height: { ideal: 480 }
            };
            
            // Use selected camera or default to front camera
            if (this.selectedCameraId) {
                videoConstraints.deviceId = { exact: this.selectedCameraId };
            } else {
                videoConstraints.facingMode = 'user'; // 'user' = kamera depan, 'environment' = kamera belakang
            }
            
            // Request camera permission
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: videoConstraints
            });
            
            // Permission granted - setup video
            this.video.srcObject = stream;
            this.stream = stream;
            
            this.video.onloadedmetadata = () => {
                this.canvas.width = this.video.videoWidth;
                this.canvas.height = this.video.videoHeight;
                this.adjustVideoSize();
                this.updateStatus('✅', 'Kamera siap digunakan');
                
                // Enable start button
                if (this.startBtn) {
                    this.startBtn.disabled = false;
                }
            };
            
        } catch (error) {
            console.error('Camera permission error:', error);
            
            if (error.name === 'NotAllowedError') {
                this.updateStatus('❌', 'Izin kamera ditolak. Klik tombol izinkan di browser.');
                this.showCameraPermissionGuide();
            } else if (error.name === 'NotFoundError') {
                this.updateStatus('❌', 'Kamera tidak ditemukan');
            } else {
                this.updateStatus('❌', 'Error: ' + error.message);
            }
        }
    }
    
    showCameraPermissionGuide() {
        const guideDiv = document.createElement('div');
        guideDiv.className = 'permission-guide';
        guideDiv.style.cssText = `
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            color: #856404;
        `;
        
        guideDiv.innerHTML = `
            <h4>📋 Cara Mengizinkan Akses Kamera:</h4>
            <ol>
                <li>Klik ikon kamera di address bar browser</li>
                <li>Pilih "Allow" atau "Izinkan"</li>
                <li>Refresh halaman jika diperlukan</li>
            </ol>
            <button id="retryCamera" class="btn btn-primary" style="margin-top: 10px;">
                🔄 Coba Lagi
            </button>
        `;
        
        const cameraContainer = document.querySelector('.camera-container');
        if (cameraContainer) {
            cameraContainer.appendChild(guideDiv);
            
            document.getElementById('retryCamera').addEventListener('click', () => {
                guideDiv.remove();
                this.requestCameraPermission();
            });
        }
    }
    
    async startDetection() {
        if (!this.stream) {
            await this.requestCameraPermission();
            if (!this.stream) return;
        }
        
        try {
            this.isDetecting = true;
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            
            this.detectionInterval = setInterval(() => {
                this.detectEmotion();
            }, 300); // Increased to 300ms (3.3 FPS) for better performance
            
            this.updateStatus('🔍', 'Mendeteksi emosi...');
        } catch (error) {
            this.resetControls();
            alert('Gagal memulai deteksi: ' + error.message);
        }
    }
    
    stopDetection() {
        this.isDetecting = false;
        
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
        
        // Hide face boxes when stopping
        this.hideFaceDetectionBox();
        
        this.resetControls();
        this.updateStatus('⏹️', 'Deteksi dihentikan');
    }
    
    async detectEmotion() {
        if (!this.isDetecting || this.video.readyState !== 4) return;
        
        // Skip frames if previous request still pending
        if (this.pendingRequest) {
            return;
        }
        
        // Frame skipping for performance
        if (this.skipFrames > 0) {
            this.skipFrames--;
            return;
        }
        
        this.pendingRequest = true;
        const startTime = performance.now(); // ⏱️ Start timing
        
        try {
            // Capture frame dari video
            const captureStart = performance.now();
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            const captureTime = performance.now() - captureStart;
            
            // Convert ke base64 dengan optimasi
            const encodeStart = performance.now();
            
            // Resize canvas untuk mengurangi ukuran data
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');
            
            // Reduce resolution untuk speed (maintain aspect ratio)
            const maxWidth = 320;  // Reduced from 640
            const maxHeight = 240; // Reduced from 480
            
            let { width, height } = this.canvas;
            if (width > maxWidth) {
                height = (height * maxWidth) / width;
                width = maxWidth;
            }
            if (height > maxHeight) {
                width = (width * maxHeight) / height;
                height = maxHeight;
            }
            
            tempCanvas.width = width;
            tempCanvas.height = height;
            tempCtx.drawImage(this.canvas, 0, 0, width, height);
            
            // Compress with lower quality for speed
            const dataURL = tempCanvas.toDataURL('image/jpeg', 0.6); // Reduced from 0.8
            const encodeTime = performance.now() - encodeStart;
            
            // Network request
            const networkStart = performance.now();
            const response = await fetch(`${this.serverUrl}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: dataURL
                })
            });
            const networkTime = performance.now() - networkStart;
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const parseStart = performance.now();
            const result = await response.json();
            const parseTime = performance.now() - parseStart;
            
            const totalTime = performance.now() - startTime;
            
            // ⏱️ Performance logging dengan adaptive rate
            if (result.success) {
                // Adaptive frame skipping berdasarkan performance
                if (totalTime > 200) {
                    this.maxSkipFrames = Math.min(4, this.maxSkipFrames + 1);
                    this.slowDetectionCount++;
                } else if (totalTime < 100 && this.maxSkipFrames > 1) {
                    this.maxSkipFrames = Math.max(1, this.maxSkipFrames - 1);
                    this.slowDetectionCount = 0;
                }
                
                // Simplified performance log
                console.log(`⚡ ${totalTime.toFixed(0)}ms | Server: ${result.processing_time || 'N/A'}ms | Skip: ${this.maxSkipFrames}`);
            }
            
            this.handleDetectionResult(result, false, totalTime);
            
            // Reset frame skipping after successful detection
            this.skipFrames = this.maxSkipFrames;
            
        } catch (error) {
            console.error('Detection error:', error);
            this.updateStatus('⚠️', 'Error deteksi: ' + error.message);
        } finally {
            this.pendingRequest = false;
        }
    }
    
    showFaceDetectionBox(faces) {
        if (!this.faceOverlay || !faces || faces.length === 0) {
            this.fadeOutFaceBoxes();
            return;
        }
        
        // Update timestamp
        this.lastSuccessfulDetection = Date.now();
        this.currentFaces = faces;
        
        // Pastikan video sudah loaded
        if (this.video.videoWidth === 0 || this.video.videoHeight === 0) {
            return;
        }
        
        // Get video element's actual displayed size
        const videoStyle = window.getComputedStyle(this.video);
        const videoDisplayWidth = parseFloat(videoStyle.width);
        const videoDisplayHeight = parseFloat(videoStyle.height);
        
        // Calculate scale factors based on actual video content vs display size
        const scaleX = videoDisplayWidth / this.video.videoWidth;
        const scaleY = videoDisplayHeight / this.video.videoHeight;
        
        // Update atau create face boxes
        this.updateOrCreateFaceBoxes(faces, scaleX, scaleY);
        
        // Set visibility
        if (!this.faceBoxVisible) {
            this.faceBoxVisible = true;
            this.faceOverlay.style.opacity = '1';
        }
        
        // Clear any existing hide timeout
        if (this.hideBoxTimeout) {
            clearTimeout(this.hideBoxTimeout);
            this.hideBoxTimeout = null;
        }
        
        // Schedule fade out only if no new detection for 3 seconds
        this.scheduleHideCheck();
    }
    
    updateOrCreateFaceBoxes(faces, scaleX, scaleY) {
        // Get existing boxes
        const existingBoxes = Array.from(this.faceOverlay.querySelectorAll('.face-box'));
        
        faces.forEach((face, index) => {
            let faceBox = existingBoxes[index];
            
            // Create new box if doesn't exist
            if (!faceBox) {
                faceBox = document.createElement('div');
                faceBox.className = 'face-box';
                this.faceOverlay.appendChild(faceBox);
            }
            
            // Get emotion color
            const emotionData = this.emotionMap[face.emotion] || { icon: '❓', color: '#00ff88' };
            const confidencePercent = Math.round(face.confidence * 100);
            
            // Calculate position and size dengan offset adjustment
            const boxX = face.x * scaleX;
            const boxY = (face.y * scaleY) + 70; // Offset 35px ke bawah (diperbesar dari 15px)
            const boxWidth = face.width * scaleX;
            const boxHeight = face.height * scaleY;
            
            // Update position and style smoothly
            faceBox.style.cssText = `
                position: absolute;
                border: 2px solid ${emotionData.color};
                border-radius: 8px;
                background: transparent;
                box-shadow: 0 0 15px ${emotionData.color}60, inset 0 0 15px ${emotionData.color}20;
                transition: all 0.2s ease-out;
                pointer-events: none;
                left: ${boxX}px;
                top: ${boxY}px;
                width: ${boxWidth}px;
                height: ${boxHeight}px;
                z-index: 15;
                opacity: 1;
            `;
            
            // Update or create label
            let emotionLabel = faceBox.querySelector('.face-label');
            if (!emotionLabel) {
                emotionLabel = document.createElement('div');
                emotionLabel.className = 'face-label';
                faceBox.appendChild(emotionLabel);
            }
            
            emotionLabel.style.cssText = `
                position: absolute;
                top: -32px;
                left: 50%;
                transform: translateX(-50%);
                background: ${emotionData.color};
                color: white;
                padding: 4px 10px;
                border-radius: 14px;
                font-size: 11px;
                font-weight: bold;
                text-align: center;
                white-space: nowrap;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                z-index: 16;
                transition: all 0.2s ease-out;
            `;
            emotionLabel.textContent = `${emotionData.icon} ${this.getEmotionLabel(face.emotion)} ${confidencePercent}%`;
        });
        
        // Remove excess boxes
        for (let i = faces.length; i < existingBoxes.length; i++) {
            existingBoxes[i].remove();
        }
    }
    
    scheduleHideCheck() {
        // Check every 100ms if boxes should be hidden
        const checkHide = () => {
            const timeSinceLastDetection = Date.now() - this.lastSuccessfulDetection;
            
            if (timeSinceLastDetection > 3000 && this.faceBoxVisible) {
                this.fadeOutFaceBoxes();
            } else if (this.faceBoxVisible && this.isDetecting) {
                setTimeout(checkHide, 100);
            }
        };
        
        setTimeout(checkHide, 100);
    }
    
    fadeOutFaceBoxes() {
        if (this.faceOverlay && this.faceBoxVisible) {
            this.faceBoxVisible = false;
            this.faceOverlay.style.transition = 'opacity 0.5s ease-out';
            this.faceOverlay.style.opacity = '0';
            
            setTimeout(() => {
                if (!this.faceBoxVisible) {
                    this.faceOverlay.innerHTML = '';
                    this.faceOverlay.style.transition = '';
                }
            }, 500);
        }
    }
    
    updateFaceBoxPositions() {
        // Update existing boxes when video size changes
        const boxes = this.faceOverlay?.querySelectorAll('.face-box');
        if (!boxes || boxes.length === 0) return;
        
        const videoStyle = window.getComputedStyle(this.video);
        const videoDisplayWidth = parseFloat(videoStyle.width);
        const videoDisplayHeight = parseFloat(videoStyle.height);
        
        const scaleX = videoDisplayWidth / this.video.videoWidth;
        const scaleY = videoDisplayHeight / this.video.videoHeight;
        
        // Re-calculate positions for existing boxes
        // This would require storing original coordinates, but for simplicity
        // we'll just clear and re-detect on resize
    }
    
    hideFaceDetectionBox() {
        this.fadeOutFaceBoxes();
        this.currentFaces = [];
        if (this.hideBoxTimeout) {
            clearTimeout(this.hideBoxTimeout);
            this.hideBoxTimeout = null;
        }
    }
    
    handleDetectionResult(result, isCapture = false, totalTime = 0) {
        this.updateStats(result, totalTime);
        
        if (result.success && result.emotions && result.emotions.length > 0) {
            const primaryEmotion = result.emotions[0];
            
            this.updateEmotionDisplay(primaryEmotion.emotion, primaryEmotion.confidence);
            this.addToHistory(primaryEmotion.emotion, primaryEmotion.confidence, isCapture);
            
            // Show face detection boxes using bounding box data dengan scale correction
            const faces = result.emotions.map(emotion => {
                // Scale coordinates back to original resolution jika image diresize
                const scaleX = this.canvas.width / 320;  // Original width / processed width
                const scaleY = this.canvas.height / 240; // Original height / processed height
                
                return {
                    x: emotion.bounding_box.x * scaleX,
                    y: emotion.bounding_box.y * scaleY,
                    width: emotion.bounding_box.width * scaleX,
                    height: emotion.bounding_box.height * scaleY,
                    emotion: emotion.emotion,
                    confidence: emotion.confidence
                };
            });
            
            this.showFaceDetectionBox(faces);
            
            this.updateStatus('✅', `${result.faces_detected} wajah terdeteksi`);
        } else {
            this.hideFaceDetectionBox();
            this.updateStatus('🔍', result.message || 'Mencari wajah...');
        }
    }
    
    updateEmotionDisplay(emotion, confidence) {
        if (!this.emotionDisplay) return;
        
        const emotionIcon = this.emotionDisplay.querySelector('.emotion-icon');
        const emotionText = this.emotionDisplay.querySelector('.emotion-text');
        const confidenceFill = this.emotionDisplay.querySelector('.confidence-fill');
        const confidenceText = this.emotionDisplay.querySelector('.confidence-text');
        
        const emotionData = this.emotionMap[emotion] || { icon: '❓', color: '#999' };
        
        if (emotionIcon) {
            emotionIcon.textContent = emotionData.icon;
            emotionIcon.style.color = emotionData.color;
        }
        
        if (emotionText) {
            emotionText.textContent = this.getEmotionLabel(emotion);
        }
        
        const confidencePercent = Math.round(confidence * 100);
        
        if (confidenceFill) {
            confidenceFill.style.width = `${confidencePercent}%`;
        }
        
        if (confidenceText) {
            confidenceText.textContent = `Akurasi: ${confidencePercent}%`;
        }
        
        // Animation
        if (emotionIcon) {
            emotionIcon.style.animation = 'none';
            setTimeout(() => {
                emotionIcon.style.animation = 'bounceIn 0.6s ease';
            }, 10);
        }
    }
    
    addToHistory(emotion, confidence, isCapture = false) {
        if (!this.historyList) return;
        
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const now = new Date();
        const time = now.toLocaleTimeString('id-ID', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
        
        const emotionData = this.emotionMap[emotion] || { icon: '❓' };
        
        historyItem.innerHTML = `
            <div class="history-emotion">${emotionData.icon}</div>
            <div class="history-details">
                <div class="history-text">${this.getEmotionLabel(emotion)}</div>
                <div class="history-time">${time} ${isCapture ? '📸' : ''}</div>
                <div class="history-confidence">Akurasi: ${Math.round(confidence * 100)}%</div>
            </div>
        `;
        
        const empty = this.historyList.querySelector('.history-empty');
        if (empty) empty.remove();
        
        this.historyList.insertBefore(historyItem, this.historyList.firstChild);
        
        const items = this.historyList.querySelectorAll('.history-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }
    
    updateStats(result, totalTime = 0) {
        this.stats.totalDetections++;
        
        if (result.success && result.emotions && result.emotions.length > 0) {
            this.stats.facesDetected++;
            this.stats.accuracySum += result.emotions[0].confidence;
        }
        
        const totalEl = document.getElementById('totalDetections');
        const facesEl = document.getElementById('facesDetected');
        const avgEl = document.getElementById('avgAccuracy');
        
        if (totalEl) totalEl.textContent = this.stats.totalDetections;
        if (facesEl) facesEl.textContent = this.stats.facesDetected;
        
        if (avgEl) {
            const avgAccuracy = this.stats.facesDetected > 0 
                ? (this.stats.accuracySum / this.stats.facesDetected * 100).toFixed(1)
                : 0;
            avgEl.textContent = `${avgAccuracy}%`;
        }
    }
    
    getEmotionLabel(emotion) {
        const labels = {
            'happy': 'Senang',
            'sad': 'Sedih',
            'neutral': 'Netral'
        };
        return labels[emotion] || 'Tidak Dikenal';
    }
    
    updateStatus(icon, message) {
        if (!this.cameraStatus) return;
        
        const statusIcon = this.cameraStatus.querySelector('.status-icon') || this.cameraStatus.querySelector('div');
        const statusText = this.cameraStatus.querySelector('span');
        
        if (statusIcon) statusIcon.textContent = icon;
        if (statusText) statusText.textContent = message;
    }
    
    adjustVideoSize() {
        if (!this.video) return;
        
        const container = this.video.parentElement;
        const containerWidth = container.clientWidth;
        
        if (containerWidth < 640) {
            this.video.style.width = '100%';
            this.video.style.height = 'auto';
        }
        
        // Clear face boxes when video size changes for accuracy
        this.hideFaceDetectionBox();
    }
    
    resetControls() {
        if (this.startBtn) this.startBtn.disabled = false;
        if (this.stopBtn) this.stopBtn.disabled = true;
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    // Animasi untuk content boxes
    const contentBoxes = document.querySelectorAll('.content-box');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    contentBoxes.forEach(box => {
        observer.observe(box);
    });
    
    // Check server connection first
    fetch('http://127.0.0.1:5000/health')
        .then(response => {
            if (response.ok) {
                console.log('✅ Server connected successfully');
                // Initialize emotion detector after server connection confirmed
                window.emotionDetector = new EmotionDetector();
            } else {
                throw new Error('Server not responding');
            }
        })
        .catch(error => {
            console.error('❌ Server connection failed:', error);
            
            // Show server connection error
            const cameraContainer = document.querySelector('.camera-container');
            if (cameraContainer) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'server-error';
                errorDiv.style.cssText = `
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    color: #721c24;
                    text-align: center;
                `;
                
                errorDiv.innerHTML = `
                    <h4>⚠️ Server Tidak Terhubung</h4>
                    <p>Pastikan server Flask berjalan di port 5000</p>
                    <button onclick="location.reload()" class="btn btn-primary">
                        🔄 Refresh Halaman
                    </button>
                `;
                
                cameraContainer.appendChild(errorDiv);
            }
        });
});

// Handle page visibility
document.addEventListener('visibilitychange', () => {
    if (window.emotionDetector) {
        if (document.hidden && window.emotionDetector.isDetecting) {
            clearInterval(window.emotionDetector.detectionInterval);
        } else if (!document.hidden && window.emotionDetector.isDetecting) {
            window.emotionDetector.detectionInterval = setInterval(() => {
                window.emotionDetector.detectEmotion();
            }, 500); // Real-time detection saat kembali aktif
        }
    }
});
