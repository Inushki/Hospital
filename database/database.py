import sqlite3
import os

# Database path
#DATABASE = 'database/patients.db'
DATABASE = "E:/TopUp/Hospital/database/patients.db"

# Uncomment this function if you want to drop the database
#def drop_database():
#    """
#    Delete the existing database if it exists.
#    """
#    if os.path.exists(DATABASE):
#        os.remove(DATABASE)
#        print("Old database file has been deleted.")

def init_db():
    """
    Initialize the database by creating the `patients` and `Doctors` tables with the correct schema.
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Create patients table
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
        
        # Create doctors table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')

         # Create staff table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS MedicalStaff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_role TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            dob TEXT NOT NULL,
            info TEXT NOT NULL
        )
        ''')
        
        print("Database and tables created successfully.")
    conn.close()

def insert_patient(name, dob, age, email, phone, medical_history, photo_path, face_data):
    """
    Insert a new patient record into the `patients` table.
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO patients (name, dob, age, email, phone, medical_history, photo_path, face_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, dob, age, email, phone, medical_history, photo_path, face_data))
        print(f"Patient {name} has been added to the database.")
    conn.close()

def get_patient_details():
    """
    Retrieve all patient records from the `patients` table.
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients')
        patients = cursor.fetchall()
        return patients

def insert_doctor(name, dob, age, email, phone, password):
    """
    Insert a new doctor record into the `Doctors` table.
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        query = '''
            INSERT INTO Doctors (name, dob, age, email, phone, password)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (name, dob, age, email, phone, password))
        print(f"Doctor {name} has been added to the database.")

def insert_medical_staff(name, dob, age, email, phone, password, info):
    """
    Insert a new medical staff record into the `MedicalStaff` table.
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        query = '''
            INSERT INTO MedicalStaff (user_role, name, dob, age, email, phone, password, info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        # Here, you need to specify 'Staff' as the user_role
        cursor.execute(query, ('Staff', name, dob, age, email, phone, password, info))
        print(f"Medical staff {name} has been added to the database.")


# Run database initialization if this script is executed directly
if __name__ == '__main__':
    # drop_database()  # Optionally drop the old database
    init_db()  # Initialize the new database
