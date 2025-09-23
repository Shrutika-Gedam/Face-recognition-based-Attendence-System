# Face-recognition-based-Attendence-System
This is a real-time face detection and attendance marking system built with Flask, OpenCV, and MongoDB. The application uses your computer's webcam to detect faces and match them against a database of registered students. When a face is recognized, it automatically records their attendance with a timestamp in a MongoDB Atlas database.

Face Detection Attendance System
A real-time attendance system using Flask, OpenCV, and MongoDB Atlas.

🌟 Features
Real-time Face Detection: Utilizes Haar Cascades from OpenCV to detect faces from a live webcam feed.
Student Registration: A simple web interface allows you to register new students by taking their photo and saving their details in a MongoDB database.
Automated Attendance Marking: When a registered face is recognized, the system automatically marks attendance with a timestamp.
GUI Status Updates: Provides real-time status messages on the web interface, confirming attendance marking.
Scalable Database: Uses MongoDB Atlas, a cloud-based NoSQL database, to efficiently store student records and attendance logs.

🚀 How It Works
The system operates in a few key stages:
Registration: A user enters a name and clicks "Register". The application captures their face from the live video feed, saves it as an image, and stores the student's name and a reference to the image in the MongoDB database.
Attendance Mode: Clicking "Start Attendance" activates the face recognition loop.
Face Recognition: The system continuously captures frames from the webcam. When a face is detected, it is compared to the registered faces in the database using a simple mean squared error (MSE) algorithm.
Attendance Marking: If a face is successfully recognized, a new attendance record containing the student's ID and a timestamp is inserted into the attendance_log collection in MongoDB. The system then automatically stops marking attendance for that student for the day.
Status Feedback: The user interface updates to show a confirmation message, such as "Attendance marked for [Student Name]!", providing immediate feedback.

🛠️ Requirements
Before you begin, ensure you have the following installed:
Python 3.x
Git (optional, but recommended for cloning the repository)
MongoDB Atlas Account (Free tier is sufficient)

📂 Project Structure
Attendence System
├── main.py                                                                                                                                                                                                          
├── database.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── scripts.js
├── dataset/
└── models/
    └── haarcascade_frontalface_default.xml

