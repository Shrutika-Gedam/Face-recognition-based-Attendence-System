from pymongo import MongoClient
import datetime
import os

# --- IMPORTANT: Replace with your actual MongoDB Atlas connection string ---
# You can find this in your MongoDB Atlas dashboard under Connect -> Connect your application.
MONGO_CONNECTION_STRING = "mongodb+srv://shrutikagedam08_db_user:Minu2001@attendance01.r8tajxd.mongodb.net/"

class DatabaseManager:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_CONNECTION_STRING)
            self.db = self.client['attendance_system']  # Database name
            self.students_collection = self.db['students']  # Collection for student details
            self.attendance_collection = self.db['attendance_log']  # Collection for attendance records
            print("Connected to MongoDB Atlas successfully!")
        except Exception as e:
            print(f"Error connecting to MongoDB Atlas: {e}")
            self.client = None

    def get_next_id(self):
        """Finds the next available unique integer ID for a new student."""
        if not self.client:
            return None
        last_student = self.students_collection.find_one(sort=[('_id', -1)])
        if last_student and 'student_id' in last_student:
            return int(last_student['student_id']) + 1
        return 1

    def register_new_student(self, name, photo_path):
        """Registers a new student with their name and the path to their photo."""
        if not self.client:
            return None
        new_id = self.get_next_id()
        if new_id is None:
            return None
        
        student_data = {
            "student_id": new_id,
            "name": name,
            "photo_path": photo_path
        }
        self.students_collection.insert_one(student_data)
        return new_id

    def get_all_students(self):
        """Fetches all registered students and their photo paths."""
        if not self.client:
            return []
        return list(self.students_collection.find())

    def mark_attendance(self, student_id):
        """Marks attendance for a student with a timestamp."""
        if not self.client:
            return
        log_entry = {
            "student_id": student_id,
            "timestamp": datetime.datetime.now()
        }
        self.attendance_collection.insert_one(log_entry)
        print(f"Attendance marked for student ID: {student_id}")

    def get_student_by_id(self, student_id):
        """Fetches a student by their ID."""
        if not self.client:
            return None
        return self.students_collection.find_one({"student_id": student_id})