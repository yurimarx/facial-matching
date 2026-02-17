from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import iris 
import numpy as np
import base64
import cv2
import json

app = Flask(__name__)
CORS(app)

IRIS_CONFIG = {
    "hostname": "facial-matching-data",
    "port": 1972,
    "namespace": "IRISAPP",
    "username": "_SYSTEM",
    "password": "SYS"
}

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
    
    embedding = DeepFace.represent(img, model_name="VGG-Face", enforce_detection=True)[0]["embedding"]
    
    analysis = DeepFace.analyze(img, actions=['age', 'gender', 'race'], enforce_detection=False)[0]
    
    return {
        "vector": embedding,
        "age": int(analysis['age']),
        "gender": analysis['dominant_gender'],
        "ethnicity": analysis['dominant_race']
    }

@app.route('/api/register', methods=['POST'])
def register():
    try:
        ssn = request.form.get('ssn')
        name = request.form.get('name')
        
        if 'image' not in request.files:
            return jsonify({"error": "Nenhum arquivo de imagem enviado"}), 400
        
        file = request.files['image']
        
        filestr = file.read()
        nparr = np.frombuffer(filestr, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        objs = DeepFace.represent(img, model_name="VGG-Face", enforce_detection=True)
        embedding = objs[0]["embedding"]
        analysis = DeepFace.analyze(img, actions=['age', 'gender', 'race'], enforce_detection=False)[0]

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

        objs = DeepFace.represent(img, model_name="VGG-Face", enforce_detection=True)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)