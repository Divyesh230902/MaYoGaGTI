from services.database_service import hash_password, db_path
import sqlite3

def register_user(username, password, role, current_stage, role_specific_field, end_goal):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    hashed_password = hash_password(password)
    
    # Handling registration based on user role (Student/Professional)
    cursor.execute('''
        INSERT INTO users (username, password, role, current_stage, role_specific_field, end_goal)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, hashed_password, role, current_stage, role_specific_field, end_goal))
    
    conn.commit()
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

    if user:
        return True
    return False