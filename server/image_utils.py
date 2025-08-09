import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import logging
from typing import List, Tuple, Dict, Any, Optional

from config import Config

logger = logging.getLogger(__name__)

class EmotionPredictor:
    """
    Advanced emotion predictor dengan noise reduction dan robust face detection
    """
    
    def __init__(self, model_path: str, cascade_path: str, preloaded_model=None):
        """
        Initialize emotion predictor
        
        Args:
            model_path: Path ke model H5
            cascade_path: Path ke Haarcascade XML
            preloaded_model: Model yang sudah di-load sebelumnya
        """
        self.model_path = model_path
        self.cascade_path = cascade_path
        
        # Load model
        if preloaded_model is not None:
            self.model = preloaded_model
            logger.info("Using preloaded model")
        else:
            self.model = self._load_model()
        
        # Load Haarcascade
        self.face_cascade = self._load_cascade()
        
        # Emotion labels sesuai dengan training
        self.emotion_labels = {
            0: "happy",
            1: "sad", 
            2: "neutral"
        }
        
        # Confidence threshold
        self.confidence_threshold = Config.CONFIDENCE_THRESHOLD
        
        logger.info("EmotionPredictor initialized successfully")
    
    def _load_model(self):
        """Load TensorFlow model dengan error handling"""
        try:
            # Try loading dengan compile=False untuk avoid optimizer issues
            model = keras.models.load_model(self.model_path, compile=False)
            
            # Recompile dengan simple optimizer
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info(f"Model loaded successfully from {self.model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_cascade(self):
        """Load Haarcascade classifier"""
        try:
            cascade = cv2.CascadeClassifier(self.cascade_path)
            
            if cascade.empty():
                raise ValueError(f"Failed to load cascade from {self.cascade_path}")
            
            logger.info(f"Haarcascade loaded successfully from {self.cascade_path}")
            return cascade
            
        except Exception as e:
            logger.error(f"Failed to load cascade: {e}")
            raise
    
    def reduce_background_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Simplified noise reduction untuk speed optimization
        """
        try:
            # Convert to grayscale untuk processing
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Simplified processing untuk speed
            processed = gray.copy()
            
            # Only essential noise reduction
            # 1. Lightweight Gaussian blur
            processed = cv2.GaussianBlur(processed, (3, 3), 0)  # Reduced kernel size
            
            # 2. Histogram equalization untuk contrast (fast operation)
            processed = cv2.equalizeHist(processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error in noise reduction: {e}")
            return image
    
    def detect_faces_multi_scale(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Optimized face detection untuk speed (reduced complexity)
        """
        try:
            # Reduce noise first
            processed_image = self.reduce_background_noise(image)
            
            # Single-scale detection untuk speed optimization
            faces = self.face_cascade.detectMultiScale(
                processed_image,
                scaleFactor=1.1,  # Fixed optimal value
                minNeighbors=4,   # Fixed optimal value
                minSize=Config.FACE_DETECTION_MIN_SIZE,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Simple duplicate removal dan size filtering
            if len(faces) > 0:
                # Convert to list dan filter berdasarkan size
                filtered_faces = []
                for (x, y, w, h) in faces:
                    # Filter faces yang terlalu kecil atau besar
                    if 30 <= w <= 300 and 30 <= h <= 300:
                        # Simple overlap check
                        is_duplicate = False
                        for (fx, fy, fw, fh) in filtered_faces:
                            # Quick overlap check
                            if (abs(x - fx) < w//2 and abs(y - fy) < h//2):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            filtered_faces.append((x, y, w, h))
                
                return filtered_faces[:3]  # Limit to 3 faces max for performance
            
            return []
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []
    
    def filter_false_positives(self, faces: List[Tuple], image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Filter false positive detections
        """
        try:
            if len(faces) == 0:
                return []
            
            filtered_faces = []
            
            for (x, y, w, h) in faces:
                # 1. Aspect ratio check (wajah umumnya persegi atau sedikit rectangular)
                aspect_ratio = w / h
                if not (0.6 <= aspect_ratio <= 1.4):
                    continue
                
                # 2. Size check
                min_size = Config.FACE_DETECTION_MIN_SIZE[0]  # Use width as minimum
                if w < min_size or h < min_size:
                    continue
                
                # 3. Variance check (area wajah harus memiliki variance yang cukup)
                try:
                    face_roi = image[y:y+h, x:x+w]
                    if face_roi.size > 0:
                        variance = np.var(face_roi)
                        if variance < 100:  # Threshold untuk variance
                            continue
                except:
                    continue
                
                # 4. Check bounds
                if x < 0 or y < 0 or x + w > image.shape[1] or y + h > image.shape[0]:
                    continue
                
                filtered_faces.append((x, y, w, h))
            
            # Remove overlapping detections (Non-Maximum Suppression sederhana)
            if len(filtered_faces) > 1:
                filtered_faces = self.non_max_suppression(filtered_faces)
            
            return filtered_faces
            
        except Exception as e:
            logger.error(f"Error in filtering false positives: {e}")
            return faces
    
    def non_max_suppression(self, faces: List[Tuple], overlap_threshold: float = 0.3) -> List[Tuple]:
        """
        Simple Non-Maximum Suppression untuk remove overlapping detections
        """
        if len(faces) == 0:
            return []
        
        # Convert to format yang lebih mudah di-process
        faces_array = np.array(faces)
        x1 = faces_array[:, 0]
        y1 = faces_array[:, 1]
        x2 = faces_array[:, 0] + faces_array[:, 2]
        y2 = faces_array[:, 1] + faces_array[:, 3]
        areas = faces_array[:, 2] * faces_array[:, 3]
        
        # Sort by area (descending)
        indices = np.argsort(areas)[::-1]
        
        keep = []
        while len(indices) > 0:
            # Take the largest area
            current = indices[0]
            keep.append(current)
            
            if len(indices) == 1:
                break
            
            # Calculate overlap dengan deteksi lainnya
            other_indices = indices[1:]
            
            # Calculate intersection
            xx1 = np.maximum(x1[current], x1[other_indices])
            yy1 = np.maximum(y1[current], y1[other_indices])
            xx2 = np.minimum(x2[current], x2[other_indices])
            yy2 = np.minimum(y2[current], y2[other_indices])
            
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            intersection = w * h
            
            # Calculate overlap ratio
            union = areas[current] + areas[other_indices] - intersection
            overlap_ratio = intersection / union
            
            # Keep detections dengan overlap ratio < threshold
            indices = other_indices[overlap_ratio <= overlap_threshold]
        
        return [faces[i] for i in keep]
    
    def preprocess_face_for_model(self, face_image: np.ndarray) -> np.ndarray:
        """
        Preprocess face image untuk model input
        """
        try:
            # Convert to grayscale jika masih color
            if len(face_image.shape) == 3:
                face_gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                face_gray = face_image
            
            # Resize ke 48x48 (sesuai training model)
            face_resized = cv2.resize(face_gray, (48, 48))
            
            # Normalize ke range [0, 1]
            face_normalized = face_resized.astype('float32') / 255.0
            
            # Add batch dan channel dimensions
            face_input = np.expand_dims(face_normalized, axis=[0, -1])
            
            return face_input
            
        except Exception as e:
            logger.error(f"Error in face preprocessing: {e}")
            return None
    
    def predict_emotion(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Main function untuk predict emotion dari image
        """
        import time
        start_time = time.time()
        
        try:
            # Detect faces
            face_detect_start = time.time()
            faces = self.detect_faces_multi_scale(image)
            face_detect_time = (time.time() - face_detect_start) * 1000
            
            if len(faces) == 0:
                return {
                    'success': False,
                    'message': 'No face detected',
                    'faces_detected': 0,
                    'emotions': [],
                    'processing_time_ms': round((time.time() - start_time) * 1000, 2)
                }
            
            results = []
            model_predict_time = 0
            
            for i, (x, y, w, h) in enumerate(faces):
                # Extract face ROI
                face_roi = image[y:y+h, x:x+w]
                
                # Preprocess untuk model
                processed_face = self.preprocess_face_for_model(face_roi)
                
                if processed_face is not None:
                    # Predict emotion
                    predict_start = time.time()
                    prediction = self.model.predict(processed_face, verbose=0)
                    predict_time = (time.time() - predict_start) * 1000
                    model_predict_time += predict_time
                    
                    predicted_class = np.argmax(prediction[0])
                    confidence = float(np.max(prediction[0]))
                    
                    emotion_result = {
                        'face_id': i + 1,
                        'bounding_box': {
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h)
                        },
                        'emotion': self.emotion_labels[predicted_class],
                        'confidence': confidence,
                        'prediction_time_ms': round(predict_time, 2),
                        'all_predictions': {
                            self.emotion_labels[j]: float(prediction[0][j]) 
                            for j in range(len(prediction[0]))
                        }
                    }
                    
                    results.append(emotion_result)
            
            total_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'faces_detected': len(faces),
                'emotions': results,
                'message': f'Successfully detected {len(faces)} face(s)',
                'processing_time_ms': round(total_time, 2),
                'timing_breakdown_ms': {
                    'face_detection': round(face_detect_time, 2),
                    'model_prediction': round(model_predict_time, 2),
                    'total': round(total_time, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in emotion prediction: {e}")
            return {
                'success': False,
                'message': f'Error during prediction: {str(e)}',
                'faces_detected': 0,
                'emotions': []
            }
