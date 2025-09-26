from flask import Flask, render_template, Response, request, jsonify
import cv2
import os
import numpy as np
from database import DatabaseManager
from datetime import datetime
import time

# --- Initialize Flask App and Database ---
app = Flask(__name__)
db_manager = DatabaseManager()
cap = cv2.VideoCapture(0)

# --- Load Haar Cascade ---
HAARCASCADE_PATH = os.path.join("models", "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(HAARCASCADE_PATH)

# --- Global Flags ---
attendance_mode = False
last_marked_time = {}
last_marked_person = None

# --- Helper Functions ---
def simple_face_recognition(face_roi):
    """Compares a live face to all stored images in the database."""
    registered_students = db_manager.get_all_students()
    if not registered_students:
        return None
        
    face_roi_resized = cv2.resize(face_roi, (150, 150))
    
    min_diff = float('inf')
    best_match = None

    for student in registered_students:
        stored_photo_path = student.get('photo_path')
        if not stored_photo_path or not os.path.exists(stored_photo_path):
            continue
        
        stored_img = cv2.imread(stored_photo_path, cv2.IMREAD_GRAYSCALE)
        if stored_img is None:
            continue

        stored_img_resized = cv2.resize(stored_img, (150, 150))
        
        diff = np.mean((face_roi_resized - stored_img_resized) ** 2)
        
        if diff < min_diff:
            min_diff = diff
            best_match = (student['name'], student['student_id'])
    
    if best_match and min_diff < 3000:
        return best_match
        
    return None

def generate_frames():
    """Generates frames from the camera for the web stream."""
    global attendance_mode, last_marked_time, last_marked_person
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        if attendance_mode:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(80, 80))
            
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                recognized_data = simple_face_recognition(face_roi)

                if recognized_data:
                    name, student_id = recognized_data
                    current_day = datetime.now().date()
                    
                    if student_id not in last_marked_time or last_marked_time[student_id] != current_day:
                        db_manager.mark_attendance(student_id)
                        last_marked_time[student_id] = current_day
                        last_marked_person = {"name": name, "student_id": student_id}
                        print(f"Attendance marked for {name} (ID: {student_id})")
                        
                        # Stop attendance mode after marking
                        attendance_mode = False
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Provides the live video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/register')
def register():
    """Handles new student registration."""
    name = request.args.get('name')
    if not name:
        return jsonify(success=False, message="Name is required.")

    success, frame = cap.read()
    if not success:
        return jsonify(success=False, message="Could not read from camera.")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))

    if len(faces) == 0:
        return jsonify(success=False, message="No face detected. Please try again.")

    (x, y, w, h) = faces[0]
    face_roi = gray[y:y+h, x:x+w]
    
    next_id = db_manager.get_next_id()
    if next_id is None:
        return jsonify(success=False, message="Database error. Check connection.")
        
    photo_path = os.path.join("dataset", f"{next_id}.jpg")
    cv2.imwrite(photo_path, face_roi)
    
    db_manager.register_new_student(name, photo_path)
    return jsonify(success=True, message=f"Registration complete for {name} with ID {next_id}.")

@app.route('/start_attendance')
def start_attendance():
    """Starts the attendance marking mode."""
    global attendance_mode, last_marked_person
    attendance_mode = True
    last_marked_person = None  # Reset the last marked person
    return jsonify(success=True, message="Looking for a face...")
    
@app.route('/get_status')
def get_status():
    """Returns the current attendance status."""
    global last_marked_person
    if last_marked_person:
        message = f"Attendance marked for {last_marked_person['name']} (ID: {last_marked_person['student_id']})."
        return jsonify(success=True, message=message)
    else:
        return jsonify(success=False, message="No attendance marked yet.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)