import os
import cv2
import numpy as np
import json
import base64
import requests
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS

# Aggressive CPU/Memory limits for free tier servers
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)

from tensorflow.keras.models import load_model
from dotenv import load_dotenv

# Load environment variables explicitly from the current folder
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app)

# Configuration from InsForge (matching exact names from frontend/.env)
INSFORGE_URL = os.environ.get("NEXT_PUBLIC_INSFORGE_BASE_URL", "https://ugs77rez.us-east.insforge.app")
INSFORGE_KEY = os.environ.get("NEXT_PUBLIC_INSFORGE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3OC0xMjM0LTU2NzgtOTBhYi1jZGVmMTIzNDU2NzgiLCJlbWFpbCI6ImFub25AaW5zZm9yZ2UuY29tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNTIyNDd9.p18_5D5QQWpKjG13fBYglhoo2alyRauAiCohnXFlYrM")

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "traffic_model.keras")
model = None
MODEL_ERROR_MSG = "Model could not be loaded"

if not os.path.exists(MODEL_PATH):
    MODEL_ERROR_MSG = f"The model file '{os.path.abspath(MODEL_PATH)}' is missing. Please run 'python traffic_model_h5.py' to generate it."
    print(MODEL_ERROR_MSG)
else:
    try:
        model = load_model(MODEL_PATH)
    except Exception as e:
        MODEL_ERROR_MSG = f"Failed to load model from {MODEL_PATH}: {e}"
        print(MODEL_ERROR_MSG)

CLASSES = ["Stop", "Speed Limit", "No Entry", "Turn Right", "Turn Left"]

def log_to_insforge(label: str, confidence: float, user_id: str):
    url = f"{INSFORGE_URL}/api/database/records/traffic_logs"
    headers = {
        "apikey": INSFORGE_KEY,
        "Authorization": f"Bearer {INSFORGE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = [{
        "predicted_label": label,
        "confidence_score": float(confidence),
        "user_id": user_id
    }]
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code not in (200, 201, 204):
            print(f"Failed to log to InsForge: {response.text}")
        else:
            print("Successfully logged to InsForge!")
    except Exception as e:
        print(f"Failed to log to InsForge: {e}")

@app.route("/predict", methods=["POST"])
def predict_traffic_sign():
    if not model:
        return jsonify({"detail": MODEL_ERROR_MSG}), 500
        
    try:
        data = request.json
        if not data or "image_base64" not in data:
            return jsonify({"detail": "Missing image_base64 in request"}), 400
            
        base64_str = data["image_base64"]
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]
            
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
             return jsonify({"detail": "Invalid image data"}), 400

        img = cv2.resize(frame, (32, 32))
        img = img / 255.0
        img = np.reshape(img, (1, 32, 32, 3))
        
        prediction = model.predict(img)
        class_index = int(np.argmax(prediction[0]))
        confidence = float(np.max(prediction[0]))
        label = CLASSES[class_index]
        
        user_id = data.get("user_id")
        if user_id:
            log_to_insforge(label, confidence, user_id)
        
        return jsonify({
            "predicted_label": label,
            "confidence_score": confidence
        })
        
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)
