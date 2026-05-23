import cv2
import os
import numpy as np
import time

# Paths
DATA_PATH = "data/faces/"
MODEL_PATH = "models/face_models/"
CASCADE_PATH = "resources/haarcascade_frontalface_default.xml"

def ensure_dirs():
    os.makedirs(DATA_PATH, exist_ok=True)
    os.makedirs(MODEL_PATH, exist_ok=True)

def capture_face(user_id):
    ensure_dirs()
    video = cv2.VideoCapture(0)
    
    try:
        facedetect = cv2.CascadeClassifier(CASCADE_PATH)
        if facedetect.empty(): raise Exception("Haarcascade not found")
    except Exception as e:
        print(f"[ERROR] {e}. Check 'resources' folder.")
        return

    count = 0
    print("[FACE] Capturing 50 images...")
    
    while True:
        ret, frame = video.read()
        if not ret: break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            count += 1
            cv2.imwrite(f"{DATA_PATH}user.{user_id}.{count}.jpg", gray[y:y+h, x:x+w])
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        cv2.imshow("Enrollment", frame)
        if count >= 50 or cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    video.release()
    cv2.destroyAllWindows()
    train_face_model(user_id)

def train_face_model(user_id):
    ensure_dirs()
    faces = []
    ids = []
    
    image_files = [f for f in os.listdir(DATA_PATH) if f.startswith(f"user.{user_id}.")]
    
    if not image_files:
        print(f"[ERROR] No face images found for User {user_id}")
        return

    print(f"[TRAIN] Training Face Model for User {user_id}...")
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    for file in image_files:
        path = os.path.join(DATA_PATH, file)
        img_numpy = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        faces.append(img_numpy)
        ids.append(int(user_id))
    
    recognizer.train(faces, np.array(ids))
    recognizer.save(f"{MODEL_PATH}user_{user_id}.yml")
    print(f"[SUCCESS] Face model saved.")

def verify_face(user_id):
    model_file = f"{MODEL_PATH}user_{user_id}.yml"
    if not os.path.exists(model_file):
        print(f"[ERROR] No model found for User {user_id}")
        return False

    print(f"[AUTH] Verifying Face for User {user_id}...")
    video = cv2.VideoCapture(0)
    facedetect = cv2.CascadeClassifier(CASCADE_PATH)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_file)
    
    t_end = time.time() + 10
    passed = False
    
    while time.time() < t_end:
        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            id, conf = recognizer.predict(gray[y:y+h, x:x+w])
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Lower confidence is better in LBPH (0 is perfect match)
            if conf < 60: 
                passed = True
                cv2.putText(frame, "MATCH", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            else:
                cv2.putText(frame, "UNKNOWN", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        
        cv2.imshow("Face Verify", frame)
        cv2.waitKey(1)
        if passed: break
            
    video.release()
    cv2.destroyAllWindows()
    return passed