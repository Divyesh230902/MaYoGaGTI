import sqlite3
import os
import hashlib
import json

# Path to the SQLite database file
db_path = os.path.join('data', 'users.db')

# Function to create the database and tables
def create_db():
    # Check if the database already exists
    if not os.path.exists(db_path):
        # Connect to the SQLite database (it will be created if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create a table for storing user information
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,                  -- Student or Professional
            role_specific_field TEXT NOT NULL,   -- Field for student stage or professional job details
            end_goal TEXT NOT NULL               -- User's end goal
        )
        ''')

        # Create a table for storing roadmaps
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            roadmap TEXT NOT NULL,               -- JSON format for storing roadmaps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create a table for storing quiz results
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            quiz_data TEXT NOT NULL,             -- JSON format for storing quiz questions and answers
            result TEXT NOT NULL,                -- User's answers in JSON format
            score REAL NOT NULL,                 -- User's score
            feedback TEXT                        -- Feedback for incorrect answers
        )
        ''')

        # Create a table for storing progress tracking
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phase TEXT NOT NULL,                 -- Phase of the roadmap (e.g., Phase 1)
            milestone TEXT NOT NULL,             -- Specific milestone the user completed
            completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()
        print("Database and tables created successfully.")
    else:
        print("Database already exists.")

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User Registration
def register_user(username, password, role, role_specific_field, end_goal):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute('''
    INSERT INTO users (username, password, role, role_specific_field, end_goal)
    VALUES (?, ?, ?, ?, ?)
    ''', (username, hashed_password, role, role_specific_field, end_goal))

    conn.commit()
    conn.close()

# User Login
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

# Get user profile
def get_user_profile(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT username, role, role_specific_field, end_goal FROM users WHERE username = ?
    ''', (username,))

    user_profile = cursor.fetchone()
    conn.close()

    if user_profile:
        return {
            'username': user_profile[0],
            'role': user_profile[1],
            'role_specific_field': user_profile[2],
            'end_goal': user_profile[3]
        }
    else:
        return None

# Update user profile
def update_user_profile(username, role, role_specific_field, end_goal):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE users SET role = ?, role_specific_field = ?, end_goal = ? WHERE username = ?
    ''', (role, role_specific_field, end_goal, username))

    conn.commit()
    conn.close()

# Save the user's roadmap in JSON format
def save_user_roadmap(username, roadmap):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    roadmap_json = json.dumps(roadmap)

    cursor.execute('''
    INSERT INTO roadmaps (username, roadmap)
    VALUES (?, ?)
    ''', (username, roadmap_json))

    conn.commit()
    conn.close()

# Get the user's roadmap history
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

# Save the quiz results
def save_quiz_results(username, quiz_data, result, score, feedback):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    quiz_data_json = json.dumps(quiz_data)
    result_json = json.dumps(result)

    cursor.execute('''
    INSERT INTO quiz_results (username, quiz_data, result, score, feedback)
    VALUES (?, ?, ?, ?, ?)
    ''', (username, quiz_data_json, result_json, score, feedback))

    conn.commit()
    conn.close()

# Track user progress for milestones
def track_user_progress(username, phase, milestone):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if this milestone is already marked as complete
    cursor.execute('''
    SELECT * FROM user_progress WHERE username = ? AND phase = ? AND milestone = ?
    ''', (username, phase, milestone))

    if not cursor.fetchone():
        # Insert the new completed milestone into the progress table
        cursor.execute('''
        INSERT INTO user_progress (username, phase, milestone)
        VALUES (?, ?, ?)
        ''', (username, phase, milestone))

        conn.commit()

    conn.close()

# Get the user's progress
def get_user_progress(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all completed milestones for the user
    cursor.execute('''
    SELECT phase, milestone FROM user_progress WHERE username = ?
    ''', (username,))

    rows = cursor.fetchall()
    conn.close()

    progress = {}
    for phase, milestone in rows:
        if phase not in progress:
            progress[phase] = []
        progress[phase].append(milestone)

    return progress