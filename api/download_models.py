from deepface import DeepFace
import numpy as np
import os

def download():
    print("⏳ Starting DeepFace models download...")
    
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

    print("Downloading VGG-Face...")
    DeepFace.represent(dummy_img, model_name="VGG-Face", enforce_detection=False, detector_backend="retinaface")

    print("Downloading Analysis models...")
    DeepFace.analyze(dummy_img, actions=['age', 'gender', 'race'], enforce_detection=False, detector_backend="retinaface")
    
    print("✅ All models downloaded successfully.")

if __name__ == "__main__":
    download()