from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import base64
import io
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import custom utilities
from image_utils import EmotionPredictor
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app, origins=Config.CORS_ORIGINS.split(',') if Config.CORS_ORIGINS != '*' else '*')

# Custom objects untuk loading model yang kompatibel
def get_custom_objects():
    """Return custom objects untuk loading model TensorFlow"""
    custom_objects = {}
    
    # Handle Nadam optimizer compatibility
    try:
        from tensorflow.keras.optimizers import Nadam, Adam
        custom_objects['Nadam'] = Nadam
        custom_objects['Adam'] = Adam
    except ImportError:
        logger.warning("Could not import Nadam/Adam optimizers")
    
    # Handle legacy optimizers
    try:
        from tensorflow.keras.optimizers.legacy import Nadam as LegacyNadam
        from tensorflow.keras.optimizers.legacy import Adam as LegacyAdam
        custom_objects['Nadam'] = LegacyNadam
        custom_objects['Adam'] = LegacyAdam
    except ImportError:
        pass
    
    return custom_objects

def load_model_safe(model_path):
    """Load model dengan error handling yang robust"""
    try:
        # Method 1: Load dengan custom objects
        logger.info(f"Attempting to load model from: {model_path}")
        custom_objects = get_custom_objects()
        model = keras.models.load_model(model_path, custom_objects=custom_objects)
        logger.info("Model loaded successfully with custom objects")
        return model
        
    except Exception as e1:
        logger.warning(f"Failed with custom objects: {e1}")
        
        try:
            # Method 2: Load tanpa custom objects
            model = keras.models.load_model(model_path, compile=False)
            logger.info("Model loaded without compilation")
            
            # Recompile dengan optimizer yang kompatibel
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            logger.info("Model recompiled with Adam optimizer")
            return model
            
        except Exception as e2:
            logger.warning(f"Failed loading without compilation: {e2}")
            
            try:
                # Method 3: Load dari JSON + weights
                json_path = model_path.replace('.h5', '.json')
                if os.path.exists(json_path):
                    logger.info(f"Attempting to load from JSON: {json_path}")
                    
                    with open(json_path, 'r') as json_file:
                        model_json = json_file.read()
                    
                    model = keras.models.model_from_json(model_json)
                    model.load_weights(model_path)
                    
                    # Compile dengan optimizer yang sederhana
                    model.compile(
                        optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    
                    logger.info("Model loaded from JSON + weights")
                    return model
                else:
                    raise FileNotFoundError(f"JSON file not found: {json_path}")
                    
            except Exception as e3:
                logger.error(f"All model loading methods failed: {e1}, {e2}, {e3}")
                return None

# Initialize predictor dengan error handling
predictor = None
try:
    logger.info("Initializing emotion predictor...")
    
    # Load model dengan safe loading
    model = load_model_safe(Config.MODEL_PATH)
    if model is None:
        raise Exception("Failed to load model with all methods")
    
    # Initialize predictor dengan model yang sudah di-load
    predictor = EmotionPredictor(
        model_path=Config.MODEL_PATH,
        cascade_path=Config.CASCADE_PATH,
        preloaded_model=model
    )
    
    logger.info("Emotion predictor initialized successfully")
    
except Exception as e:
    logger.error(f"Error initializing predictor: {e}")
    logger.error(f"Failed to initialize predictor: {e}")
    predictor = None

@app.route('/')
def index():
    """API information endpoint"""
    return jsonify({
        'name': 'Neo Telemetri Facial Emotion Recognition API',
        'version': '1.0.0',
        'status': 'active' if predictor else 'error',
        'endpoints': {
            'health': 'GET /',
            'predict': 'POST /predict',
            'predict_file': 'POST /predict_file'
        },
        'supported_emotions': ['happy', 'sad', 'neutral']
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if predictor else 'unhealthy',
        'predictor_status': 'initialized' if predictor else 'failed',
        'timestamp': tf.timestamp().numpy().item()
    })

@app.route('/predict', methods=['POST'])
def predict_emotion():
    """Predict emotion from base64 encoded image"""
    import time
    start_time = time.time()  # ⏱️ Start timing
    
    if not predictor:
        return jsonify({'error': 'Predictor not initialized'}), 500
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        decode_start = time.time()
        image_data = data['image']
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        decode_time = (time.time() - decode_start) * 1000
        
        # Convert RGB to BGR for OpenCV
        convert_start = time.time()
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        convert_time = (time.time() - convert_start) * 1000
        
        # Predict emotion
        predict_start = time.time()
        results = predictor.predict_emotion(image_array)
        predict_time = (time.time() - predict_start) * 1000
        
        total_time = (time.time() - start_time) * 1000
        
        # ⏱️ Add timing info to response
        results['processing_time'] = round(total_time, 2)
        results['timing_breakdown'] = {
            'decode_ms': round(decode_time, 2),
            'convert_ms': round(convert_time, 2), 
            'predict_ms': round(predict_time, 2),
            'total_ms': round(total_time, 2)
        }
        
        logger.info(f"🔥 Server Processing: {total_time:.1f}ms (decode: {decode_time:.1f}ms, predict: {predict_time:.1f}ms)")
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in predict_emotion: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict_file', methods=['POST'])
def predict_emotion_file():
    """Predict emotion from uploaded file"""
    if not predictor:
        return jsonify({'error': 'Predictor not initialized'}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image file
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Predict emotion
        results = predictor.predict_emotion(image_array)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in predict_emotion_file: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=Config.FLASK_DEBUG, host=Config.HOST, port=Config.PORT)
