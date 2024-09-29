import sqlite3
import os
import json
import hashlib

# Path to the SQLite database file
db_path = os.path.join('data', 'users.db')

# Function to create the database and tables
def create_db():
    # Check if the database already exists
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            current_stage TEXT NOT NULL,
            field_of_study TEXT NOT NULL,
            end_goal TEXT NOT NULL
        )
        ''')

        # Create table to store roadmaps
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            roadmap TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
        ''')

        # Create table to store quiz results
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phase TEXT NOT NULL,
            quiz_data TEXT NOT NULL,
            score INTEGER NOT NULL,
            is_passed BOOLEAN NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
        ''')

        # Create table to store user progress
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phase TEXT NOT NULL,
            milestone TEXT NOT NULL,
            is_completed BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
        ''')

        # Create table to store gap analysis/feedback
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gap_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phase TEXT NOT NULL,
            feedback TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
        ''')

        conn.commit()
        conn.close()
        print("Database and tables created successfully.")
    else:
        print("Database already exists.")

# User registration and login
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, role, current_stage, field_of_study, end_goal):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute('''
        INSERT INTO users (username, password, role, current_stage, field_of_study, end_goal)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, hashed_password, role, current_stage, field_of_study, end_goal))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Username already exists.")
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute('''
    SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, hashed_password))

    user = cursor.fetchone()
    conn.close()

    return user



# Retrieve user profile
def get_user_profile(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT username, role, current_stage, field_of_study, end_goal FROM users WHERE username = ?
    ''', (username,))
    
    user_profile = cursor.fetchone()
    conn.close()

    if user_profile:
        return {
            "username": user_profile[0],
            "role": user_profile[1],
            "current_stage": user_profile[2],
            "field_of_study": user_profile[3],
            "end_goal": user_profile[4]
        }
    return None

# Update user profile
def update_user_profile(username, field_of_study, end_goal):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE users 
    SET field_of_study = ?, end_goal = ?
    WHERE username = ?
    ''', (field_of_study, end_goal, username))

    conn.commit()
    conn.close()

# Save user's roadmap in the database
def save_user_roadmap(username, roadmap):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Convert roadmap dictionary to JSON string
    roadmap_json = json.dumps(roadmap)

    cursor.execute('''
    INSERT INTO roadmaps (username, roadmap)
    VALUES (?, ?)
    ''', (username, roadmap_json))

    conn.commit()
    conn.close()

# Get user's roadmap history
def get_user_roadmap(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT roadmap FROM roadmaps WHERE username = ? ORDER BY id DESC LIMIT 1
    ''', (username,))

    roadmap = cursor.fetchone()
    conn.close()

    if roadmap:
        return json.loads(roadmap[0])
    return None

# Roadmap functions
def save_user_roadmap(username, roadmap_json):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO roadmaps (username, roadmap)
    VALUES (?, ?)
    ''', (username, json.dumps(roadmap_json)))

    conn.commit()
    conn.close()

def get_user_roadmap(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT roadmap FROM roadmaps WHERE username = ? ORDER BY created_at DESC LIMIT 1
    ''', (username,))

    roadmap = cursor.fetchone()
    conn.close()

    if roadmap:
        return json.loads(roadmap[0])
    else:
        return None

# Quiz and progress tracking
def save_quiz_results(username, phase, quiz_data, score, is_passed):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO quiz_results (username, phase, quiz_data, score, is_passed)
    VALUES (?, ?, ?, ?, ?)
    ''', (username, phase, json.dumps(quiz_data), score, is_passed))

    conn.commit()
    conn.close()

def track_user_progress(username, phase, milestone, is_completed):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO user_progress (username, phase, milestone, is_completed)
    VALUES (?, ?, ?, ?)
    ''', (username, phase, milestone, is_completed))

    conn.commit()
    conn.close()

def get_user_progress(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT phase, milestone, is_completed FROM user_progress WHERE username = ?
    ''', (username,))

    progress = cursor.fetchall()
    conn.close()

    return progress

# Gap analysis/feedback functions
def save_gap_analysis(username, phase, feedback):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO gap_analysis (username, phase, feedback)
    VALUES (?, ?)
    ''', (username, phase, json.dumps(feedback)))

    conn.commit()
    conn.close()

def get_gap_analysis(username, phase):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT feedback FROM gap_analysis WHERE username = ? AND phase = ?
    ''', (username, phase))

    feedback = cursor.fetchone()
    conn.close()

    if feedback:
        return json.loads(feedback[0])
    else:
        return None