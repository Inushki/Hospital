from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import base64
import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance
from database.database import insert_doctor



app = Flask(__name__)

# MediaPipe face detection setup
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Directory for photos
PHOTO_DIRECTORY = 'static/photos'
if not os.path.exists(PHOTO_DIRECTORY):
    os.makedirs(PHOTO_DIRECTORY)

# Database setup
#DATABASE = "E:/TopUp/Hospital/patients.db"
DATABASE = "E:/TopUp/Hospital/database/patients.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            medical_history TEXT NOT NULL,
            photo_path TEXT,
            face_data TEXT
        )
        ''')
    conn.close()

def insert_patient(name, dob, age, email, phone, medical_history, photo_path, face_data):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO patients (name, dob, age, email, phone, medical_history, photo_path, face_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, dob, age, email, phone, medical_history, photo_path, face_data))
    conn.close()

def get_patient_details():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients')
        return cursor.fetchall()

def extract_face_features(image):
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.detections:
            face_landmarks = results.detections[0].location_data.relative_keypoints
            feature_vector = np.array([[point.x, point.y] for point in face_landmarks]).flatten()
            return feature_vector
    return None

def compare_faces(registered_face_data, captured_face_data):
    registered_face_vector = np.array(eval(registered_face_data))
    captured_face_vector = np.array(captured_face_data)
    
    # Calculate the Euclidean distance between the two vectors
    dist = distance.euclidean(registered_face_vector, captured_face_vector)
    
    # Set a threshold for what is considered a "match"
    return dist < 0.1  # Adjust this threshold as necessary

@app.route('/')
def index():
    return render_template('index.html')


# Database connection helper function
def get_db_connection():
    conn = sqlite3.connect('patients.db')  # Change to your database file path
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# Authentication function using the Users table
def authenticate_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query the Users table to validate the email and password
    query = "SELECT * FROM Users WHERE Email = ? AND Password = ?"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {"success": True, "UserRole": user["UserRole"]}  # Assuming 'role' exists in Users table
    else:
        return {"success": False}

# Route for login page
# Login route

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Variable to hold error message
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = authenticate_user(email, password)

        if user:
            return redirect(url_for('doctor_dashboard'))  # Redirect to dashboard on success
        else:
            error = "Invalid email or password"  # Set error message on failure

    return render_template('login.html', error=error)  # Pass error message to template

@app.route('/doctor_dashboard')
def doctor_dashboard():
    return render_template('doctor_dashboard.html')

# Route for dashboard redirection based on role
# @app.route('/dashboard')
# def dashboard(role):
#     return f"Welcome to the Dashboard!"





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        age = request.form['age']
        email = request.form['email']
        phone = request.form['phone']
        medical_history = request.form['medical_history']

        # Initialize photo_path and face_data to None
        photo_path = None
        face_data = None

        try:
            # Handle uploaded photo
            if 'photo' in request.files and request.files['photo'].filename != '':
                uploaded_photo = request.files['photo']
                photo_path = os.path.join(PHOTO_DIRECTORY, f'{name}_{phone}.png')
                uploaded_photo.save(photo_path)

                # Load the image and extract face features
                image = cv2.imread(photo_path)
                face_data = extract_face_features(image)
                if face_data is not None:
                    face_data = str(face_data.tolist())

            # Handle captured photo
            captured_photo_data = request.form.get('captured_photo')
            if captured_photo_data:
                photo_data = base64.b64decode(captured_photo_data.split(',')[1])
                photo_path = os.path.join(PHOTO_DIRECTORY, f'{name}_{phone}.png')
                with open(photo_path, 'wb') as f:
                    f.write(photo_data)

                # Load the image and extract face features
                image = cv2.imread(photo_path)
                face_data = extract_face_features(image)
                if face_data is not None:
                    face_data = str(face_data.tolist())

            # Verify if the photo was saved successfully
            if photo_path and not os.path.exists(photo_path):
                return render_template('patientRegistration.html', message="Error: Photo was not saved successfully.")

            if face_data is None:
                return render_template('patientRegistration.html', message="Error: No face detected in the image.")

            # Insert patient details into the database
            insert_patient(name, dob, age, email, phone, medical_history, photo_path, face_data)

            return render_template('status.html', message="Patient registered successfully!")

        except Exception as e:
            return render_template('patientRegistration.html', message=f"Error during registration: {str(e)}")

    return render_template('patientRegistration.html')

@app.route('/search_patient', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        captured_photo_data = request.form.get('captured_photo')

        # Decode the captured photo
        if not captured_photo_data:
            return render_template('search.html', message="No photo data received.")

        try:
            captured_photo = base64.b64decode(captured_photo_data.split(',')[1])
            captured_img_array = np.frombuffer(captured_photo, np.uint8)
            captured_img = cv2.imdecode(captured_img_array, cv2.IMREAD_COLOR)

            if captured_img is None:
                return render_template('search.html', message="Failed to decode the captured image.")
        except Exception as e:
            return render_template('search.html', message=f"Error processing the captured photo: {str(e)}")

        # Extract features from the captured image
        captured_face_data = extract_face_features(captured_img)
        if captured_face_data is None:
            return render_template('search.html', message="No face detected in the captured image.")

        # Compare the captured face with registered faces
        patients = get_patient_details()
        for patient in patients:
            if patient[8]:  # If there's face data
                if compare_faces(patient[8], captured_face_data):
                    return render_template('search.html', message="Patient found!", patient=patient)

        return render_template('search.html', message="Patient not found.")

    return render_template('search.html')

  # The login page template

@app.route('/patientRegistration', methods=['GET', 'POST'])
def patientRegistration():
    return render_template('patientRegistration.html')  # The login page template

@app.route('/doctor_register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        # Extract the required fields from the form
        name = request.form['name']
        dob = request.form['dob']  # Date of birth
        age = request.form['age']  # Age
        email = request.form['email']  # Email
        phone = request.form['phone']  # Phone number
        password = request.form['password']  # Password

        try:
            # Insert the doctor record using the insert_doctor function
            insert_doctor(name, dob, age, email, phone, password)
            return jsonify({'success': True}), 200  # Success response
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400  # Error response

    return render_template('doctor_register.html')



@app.route('/all_patients')
def patients():
    all_patients = get_patient_details()
    return render_template('all_patients.html', patients=all_patients)
 
def insert_medical_staff(user_role, name, email, phone, password, dob, info):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO MedicalStaff (user_role, name, email, phone, password, dob, info) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (user_role, name, email, phone, password, dob, info))
        connection.commit()
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


@app.route('/medical_staff_register', methods=['GET', 'POST'])
def medical_staff_register():
    if request.method == 'POST':
        # Extract form data
        user_role = "Staff"  # Static user role
        name = request.form['name']
        email = request.form['email']
        phone = request.form['contact']
        password = request.form['password']
        dob = request.form['dob']
        info = request.form['message']  # Placeholder for additional info

        # Validate input data
        if not all([name, email, phone, password, dob]):
            return render_template('medical_staff_register.html', message='All fields are required.', success=False)

        try:
            # Insert the medical staff record
            insert_medical_staff(user_role, name, email, phone, password, dob, info)
            return render_template('medical_staff_register.html', message='Registration successful!', success=True)
        except Exception as e:
            return render_template('medical_staff_register.html', message=str(e), success=False)

    # Render the registration form
    return render_template('medical_staff_register.html')





def get_patient_details_by_id(patient_id):
    patients = get_patient_details()  # Fetch the latest patient details from the database
    for patient in patients:
        if patient[0] == patient_id:
            return {
                'id': patient[0],
                'name': patient[1],
                'dob': patient[2],
                'age': patient[3],
                'email': patient[4],
                'phone': patient[5],
                'medical_history': patient[6]
            }
    return None

def get_patient_report(patient_id):
    # Fetch patient data from the patients table
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Use 'id' as the correct column name
    query = "SELECT * FROM patients WHERE id = ?"
    cursor.execute(query, (patient_id,))
    patient_data = cursor.fetchone()  # Fetch one record
    
    cursor.close()
    connection.close()
    
    return patient_data  # Return the patient data

@app.route('/patient/<int:patient_id>')
def patient_report(patient_id):
    patient = get_patient_report(patient_id)
    if patient:
        return render_template('patient_report.html', patient=patient)
    else:
        return render_template('patient_report.html', patient=None)

# @app.route('/view_report/<int:patient_id>', endpoint='view_patient_report_unique')
# def view_patient_report(patient_id):
#     # Logic to retrieve the patient report
#     patient_report = get_patient_report(patient_id)  # Ensure this function is defined
#     return render_template('report.html', report=patient_report)  # Use your actual template



@app.route('/all_patients')
def list_patients():  # Changed the function name to avoid conflicts
    return render_template('all_patients.html', patients=patients_data)

@app.route('/view_report/<int:patient_id>')
def view_patient_report(patient_id):  # Changed the function name to avoid conflicts
    patient_details = get_patient_details_by_id(patient_id)
    if patient_details:
        return render_template('report.html', patient=patient_details)
    else:
        return render_template('report.html', message="Patient not found.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
