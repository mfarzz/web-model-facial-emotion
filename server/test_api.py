import requests
import base64
import json
import cv2
import numpy as np
from PIL import Image
import io

class EmotionAPIClient:
    """
    Client untuk testing Neo Telemetri Emotion Recognition API
    """
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def encode_image_to_base64(self, image_path):
        """
        Convert image file to base64 string
        """
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    
    def predict_from_file(self, image_path):
        """
        Predict emotion from image file path
        """
        try:
            # Encode image
            image_b64 = self.encode_image_to_base64(image_path)
            
            # Prepare request
            payload = {
                "image": f"data:image/jpeg;base64,{image_b64}"
            }
            
            # Send request
            response = requests.post(
                f"{self.base_url}/predict",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    def predict_from_webcam(self, duration=5):
        """
        Capture from webcam and predict emotion
        """
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return {"error": "Could not open webcam"}
        
        print(f"Capturing from webcam for {duration} seconds...")
        
        # Capture frame after few seconds
        import time
        time.sleep(2)
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return {"error": "Could not capture frame"}
        
        # Convert to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Predict
        payload = {
            "image": f"data:image/jpeg;base64,{image_b64}"
        }
        
        response = requests.post(
            f"{self.base_url}/predict",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def test_noisy_background(self, image_path):
        """
        Test with artificially noisy background
        """
        # Load image
        image = cv2.imread(image_path)
        
        # Add noise to background
        h, w = image.shape[:2]
        noise = np.random.randint(0, 50, (h, w, 3), dtype=np.uint8)
        noisy_image = cv2.add(image, noise)
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', noisy_image)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # Predict
        payload = {
            "image": f"data:image/jpeg;base64,{image_b64}"
        }
        
        response = requests.post(
            f"{self.base_url}/predict",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def health_check(self):
        """
        Check API health
        """
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    """
    Main testing function
    """
    client = EmotionAPIClient()
    
    print("Neo Telemetri Emotion Recognition API Test")
    print("=" * 50)
    
    # Health check
    print("1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    print()
    
    # Test with image file (you need to provide an image)
    # Uncomment and modify path as needed
    # print("2. Test with image file:")
    # result = client.predict_from_file("path/to/your/test/image.jpg")
    # print(json.dumps(result, indent=2))
    # print()
    
    # Test with webcam
    print("3. Test with webcam:")
    try:
        webcam_result = client.predict_from_webcam()
        print(json.dumps(webcam_result, indent=2))
    except Exception as e:
        print(f"Webcam test failed: {str(e)}")
    print()
    
    # Test noisy background (uncomment when you have an image)
    # print("4. Test with noisy background:")
    # noisy_result = client.test_noisy_background("path/to/your/test/image.jpg")
    # print(json.dumps(noisy_result, indent=2))

if __name__ == "__main__":
    main()
