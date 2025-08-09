#!/usr/bin/env python3
"""
Neo Telemetri Facial Emotion Recognition Server
Startup script with configuration options
"""

import os
import sys
import argparse
from app import app, predictor
from config import Config

def main():
    parser = argparse.ArgumentParser(description='Neo Telemetri Emotion Recognition Server')
    parser.add_argument('--host', default=Config.HOST, help='Host to bind to')
    parser.add_argument('--port', type=int, default=Config.PORT, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--model-path', default=Config.MODEL_PATH, help='Path to emotion model')
    parser.add_argument('--cascade-path', default=Config.CASCADE_PATH, help='Path to Haarcascade file')
    parser.add_argument('--env-file', default='.env', help='Path to environment file')
    
    args = parser.parse_args()
    
    # Load environment file if specified
    if args.env_file and os.path.exists(args.env_file):
        from dotenv import load_dotenv
        load_dotenv(args.env_file)
        print(f"Loaded environment from: {args.env_file}")
    
    # Validate configuration paths
    try:
        Config.validate_paths()
        print("✓ All required files found")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Check if model files exist
    if not os.path.exists(args.model_path):
        print(f"Error: Model file not found at {args.model_path}")
        print("Please ensure the model.h5 file is in the correct location.")
        sys.exit(1)
    
    if not os.path.exists(args.cascade_path):
        print(f"Error: Haarcascade file not found at {args.cascade_path}")
        print("Please ensure the haarcascade_frontalface_default.xml file is in the correct location.")
        sys.exit(1)
    
    # Check if predictor is initialized
    if predictor is None:
        print("Error: Failed to initialize emotion predictor")
        print("Please check the model and cascade file paths")
        sys.exit(1)
    
    print("=" * 60)
    print("Neo Telemetri Facial Emotion Recognition Server")
    print("=" * 60)
    print(f"Model path: {args.model_path}")
    print(f"Cascade path: {args.cascade_path}")
    print(f"Server: http://{args.host}:{args.port}")
    print("=" * 60)
    print("Features:")
    print("✓ Advanced noise reduction")
    print("✓ Multi-scale face detection")
    print("✓ False positive filtering")
    print("✓ Real-time emotion recognition")
    print("✓ Support for noisy backgrounds")
    print("=" * 60)
    print("API Endpoints:")
    print("  GET  /         - API information")
    print("  GET  /health   - Health check")
    print("  POST /predict  - Predict emotion from base64 image")
    print("  POST /predict_file - Predict emotion from uploaded file")
    print("=" * 60)
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or Config.FLASK_DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Server stopped by user")
        print("=" * 60)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
