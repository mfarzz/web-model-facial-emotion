import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Server configuration
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Model configuration with fallback paths
    MODEL_PATH = os.environ.get('MODEL_PATH')
    MODEL_JSON_PATH = os.environ.get('MODEL_JSON_PATH')
    CASCADE_PATH = os.environ.get('CASCADE_PATH')

    # Image processing configuration
    MAX_IMAGE_SIZE = int(os.environ.get('MAX_IMAGE_SIZE', 5 * 1024 * 1024))  # Default 5MB
    MIN_FACE_SIZE = int(os.environ.get('MIN_FACE_SIZE', 30))
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', 0.7))
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,bmp').split(','))
    
    # Face detection parameters
    FACE_DETECTION_SCALE_FACTOR = float(os.environ.get('SCALE_FACTOR', 1.1))
    FACE_DETECTION_MIN_NEIGHBORS = int(os.environ.get('MIN_NEIGHBORS', 5))
    FACE_DETECTION_MIN_SIZE = (
        int(os.environ.get('MIN_SIZE_WIDTH', 30)), 
        int(os.environ.get('MIN_SIZE_HEIGHT', 30))
    )
    
    # Noise reduction parameters
    ENABLE_GAUSSIAN_BLUR = os.environ.get('ENABLE_GAUSSIAN_BLUR', 'True').lower() == 'true'
    ENABLE_BILATERAL_FILTER = os.environ.get('ENABLE_BILATERAL_FILTER', 'True').lower() == 'true'
    ENABLE_MORPHOLOGICAL_OPS = os.environ.get('ENABLE_MORPHOLOGICAL_OPS', 'True').lower() == 'true'
    
    GAUSSIAN_KERNEL_SIZE = int(os.environ.get('GAUSSIAN_KERNEL_SIZE', 5))
    GAUSSIAN_BLUR_KERNEL = (GAUSSIAN_KERNEL_SIZE, GAUSSIAN_KERNEL_SIZE)
    
    BILATERAL_FILTER_D = int(os.environ.get('BILATERAL_D', 9))
    BILATERAL_FILTER_SIGMA_COLOR = int(os.environ.get('BILATERAL_SIGMA_COLOR', 75))
    BILATERAL_FILTER_SIGMA_SPACE = int(os.environ.get('BILATERAL_SIGMA_SPACE', 75))
    
    # API Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/server.log')
    ENABLE_FILE_LOGGING = os.environ.get('ENABLE_FILE_LOGGING', 'False').lower() == 'true'
    
    # Performance Settings
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 4))
    DETECTION_TIMEOUT = int(os.environ.get('DETECTION_TIMEOUT', 30))
    PROCESSING_CACHE_SIZE = int(os.environ.get('PROCESSING_CACHE_SIZE', 100))
    
    # Security Settings
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    ENABLE_CSRF_PROTECTION = os.environ.get('ENABLE_CSRF_PROTECTION', 'False').lower() == 'true'
    ENABLE_CORS = os.environ.get('ENABLE_CORS', 'True').lower() == 'true'
    
    # Development Settings
    ENABLE_PROFILING = os.environ.get('ENABLE_PROFILING', 'False').lower() == 'true'
    ENABLE_DETAILED_ERRORS = os.environ.get('ENABLE_DETAILED_ERRORS', 'True').lower() == 'true'
    
    @classmethod
    def validate_paths(cls):
        """Validate that required model files exist"""
        missing_files = []
        
        if not os.path.exists(cls.MODEL_PATH):
            missing_files.append(f"Model file: {cls.MODEL_PATH}")
        
        if not os.path.exists(cls.CASCADE_PATH):
            missing_files.append(f"Cascade file: {cls.CASCADE_PATH}")
            
        if missing_files:
            raise FileNotFoundError(f"Missing required files:\n" + "\n".join(missing_files))
        
        return True
    
    @classmethod 
    def get_model_info(cls):
        """Get model configuration information"""
        return {
            'model_path': cls.MODEL_PATH,
            'model_json_path': cls.MODEL_JSON_PATH,
            'cascade_path': cls.CASCADE_PATH,
            'confidence_threshold': cls.CONFIDENCE_THRESHOLD,
            'face_detection': {
                'scale_factor': cls.FACE_DETECTION_SCALE_FACTOR,
                'min_neighbors': cls.FACE_DETECTION_MIN_NEIGHBORS,
                'min_size': cls.FACE_DETECTION_MIN_SIZE
            },
            'noise_reduction': {
                'gaussian_blur': cls.ENABLE_GAUSSIAN_BLUR,
                'bilateral_filter': cls.ENABLE_BILATERAL_FILTER,
                'morphological_ops': cls.ENABLE_MORPHOLOGICAL_OPS
            }
        }
