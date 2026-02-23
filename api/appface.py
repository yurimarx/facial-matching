from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import iris 
import numpy as np
import base64
import cv2
import json
import threading

app = Flask(__name__)
CORS(app)

MODEL_STATUS = "pending"

IRIS_CONFIG = {
    "hostname": "facial-matching-data",
    "port": 1972,
    "namespace": "IRISAPP",
    "username": "_SYSTEM",
    "password": "SYS"
}

def warm_up_models():
    global MODEL_STATUS
    MODEL_STATUS = "loading"
    try:
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

        DeepFace.represent(dummy_img, model_name="VGG-Face", enforce_detection=False, detector_backend="retinaface")

        DeepFace.analyze(dummy_img, actions=['age', 'gender', 'race'], enforce_detection=False, detector_backend="retinaface")
        MODEL_STATUS = "ready"
    except Exception as e:
        print(f"Error during warm-up: {e}")
        MODEL_STATUS = "error"

def get_iris_connection():
    return iris.connect(
        IRIS_CONFIG["hostname"],
        IRIS_CONFIG["port"],
        IRIS_CONFIG["namespace"],
        IRIS_CONFIG["username"],
        IRIS_CONFIG["password"]
    )

def extract_face_info(img_base64):
    encoded_data = img_base64.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    embedding = DeepFace.represent(img, model_name="VGG-Face", enforce_detection=True, detector_backend="retinaface")[0]["embedding"]
    
    analysis = DeepFace.analyze(img, actions=['age', 'gender', 'race'], enforce_detection=False, detector_backend="retinaface")[0]
    
    return {
        "vector": embedding,
        "age": int(analysis['age']),
        "gender": analysis['dominant_gender'],
        "ethnicity": analysis['dominant_race']
    }

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": MODEL_STATUS})

@app.route('/api/register', methods=['POST'])
def register():
    try:
        ssn = request.form.get('ssn')
        name = request.form.get('name')
        
        if 'image' not in request.files:
            return jsonify({"error": "No file sent"}), 400
        
        file = request.files['image']
        
        filestr = file.read()
        nparr = np.frombuffer(filestr, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        objs = DeepFace.represent(img, model_name="VGG-Face", enforce_detection=True, detector_backend="retinaface")
        embedding = objs[0]["embedding"]
        analysis = DeepFace.analyze(img, actions=['age', 'gender', 'race'], enforce_detection=False, detector_backend="retinaface")[0]

        conn = get_iris_connection()
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO dc_facialmatching.FacialData 
            (SSN, Name, Age, Gender, Ethnicity, FaceVector) 
            VALUES (?, ?, ?, ?, ?, TO_VECTOR(?))
        """
        cursor.execute(sql, (
            ssn, name, int(analysis['age']), 
            analysis['dominant_gender'], analysis['dominant_race'], 
            json.dumps(embedding)
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", 
                        "person": {"Gender" : analysis['dominant_gender'], 
                                   "Age": analysis['age'], 
                                   "Ethnicity": analysis['dominant_race']}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify', methods=['POST'])
def verify():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No file sent"}), 400
        
        file = request.files['image']
        
        filestr = file.read()
        nparr = np.frombuffer(filestr, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Invalid file"}), 400

        objs = DeepFace.represent(img, model_name="VGG-Face", enforce_detection=True, detector_backend="retinaface")
        current_vector = objs[0]["embedding"]
        
        conn = get_iris_connection()
        cursor = conn.cursor()
        
        sql = """
            SELECT TOP 1 SSN, Name, Age, Gender, Ethnicity,
                   VECTOR_DOT_PRODUCT(FaceVector, TO_VECTOR(?)) as similarity
            FROM dc_facialmatching.FacialData
            ORDER BY similarity DESC
        """
        cursor.execute(sql, (json.dumps(current_vector),))
        row = cursor.fetchone()
        
        result_data = None
        if row:
            result_data = {
                "match": True,
                "similarity": float(row[5]),
                "person": {
                    "ssn": row[0],
                    "name": row[1],
                    "age": row[2],
                    "gender": row[3],
                    "ethnicity": row[4]
                }
            }
        
        cursor.close()
        conn.close()
        
        if result_data and result_data["similarity"] > 0.80:
            return jsonify({
                "match": True,
                "person": result_data["person"],
                "confidence": result_data["similarity"]
            })
        else:
            return jsonify({"match": False, 
                            "confidence": result_data["similarity"], 
                            "message": "Unknown person"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/people', methods=['GET'])
def list_people():
    try:
        conn = get_iris_connection()
        cursor = conn.cursor()
        
        sql = "SELECT SSN, Name, Age, Gender, Ethnicity FROM dc_facialmatching.FacialData"
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        people = []
        for row in rows:
            people.append({
                "ssn": row[0],
                "name": row[1],
                "age": row[2],
                "gender": row[3],
                "ethnicity": row[4]
            })
            
        cursor.close()
        conn.close()
        return jsonify({"people": people})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify_family', methods=['POST'])
def verify_family():
    try:
        if 'father_image' not in request.files or \
           'child_image' not in request.files or \
           'mother_image' not in request.files:
            return jsonify({"error": "Please upload all three images (father, child, mother)"}), 400

        father_file = request.files['father_image']
        child_file = request.files['child_image']
        mother_file = request.files['mother_image']

        father_img = cv2.imdecode(np.frombuffer(father_file.read(), np.uint8), cv2.IMREAD_COLOR)
        child_img = cv2.imdecode(np.frombuffer(child_file.read(), np.uint8), cv2.IMREAD_COLOR)
        mother_img = cv2.imdecode(np.frombuffer(mother_file.read(), np.uint8), cv2.IMREAD_COLOR)

        if father_img is None or child_img is None or mother_img is None:
            return jsonify({"error": "One or more images are invalid"}), 400

        father_verification = DeepFace.verify(
            img1_path=child_img,
            img2_path=father_img,
            model_name="VGG-Face",
            detector_backend="retinaface",
            enforce_detection=True
        )

        mother_verification = DeepFace.verify(
            img1_path=child_img,
            img2_path=mother_img,
            model_name="VGG-Face",
            detector_backend="retinaface",
            enforce_detection=True
        )

        father_similarity = 1 - father_verification['distance']
        mother_similarity = 1 - mother_verification['distance']

        return jsonify({
            "resemblance_to_father": father_similarity * 100,
            "resemblance_to_mother": mother_similarity * 100
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    threading.Thread(target=warm_up_models).start()
    app.run(host='0.0.0.0', port=5000, debug=True)