from deepface import DeepFace
import numpy as np
import os

def download():
    print("⏳ Starting DeepFace models download...")
    
    # Create a dummy image to trigger the model loading/downloading
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

    # Trigger VGG-Face model download
    print("Downloading VGG-Face...")
    DeepFace.represent(dummy_img, model_name="VGG-Face", enforce_detection=False)

    # Trigger Age, Gender, Race models download
    print("Downloading Analysis models...")
    DeepFace.analyze(dummy_img, actions=['age', 'gender', 'race'], enforce_detection=False)
    
    print("✅ All models downloaded successfully.")

if __name__ == "__main__":
    download()