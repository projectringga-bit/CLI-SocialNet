import sqlite3
import os
import hashlib
import secrets

db_connection = None

def connect_db():
    global db_connection

    db_connection = sqlite3.connect("socialnet.db")
    db_connection.row_factory = sqlite3.Row

    return db_connection

def close_db():
    global db_connection
    if db_connection is not None:
        db_connection.close()
        db_connection = None

def init_db():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users (" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                    "username TEXT UNIQUE NOT NULL," \
                    "password_hash TEXT NOT NULL," \
                    "password_salt TEXT NOT NULL)" )
    connection.commit()

    return True

def create_user(username, password): #TODO: limit or email verification
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username.lower(),))
    if cursor.fetchone() is not None:
        print(f"Error: Username is already taken.")
        return False
    
    def hash_password(password, salt=None):
        if salt is None:
            salt = secrets.token_hex(32)
        
        pass_salt = password + salt
        hash = hashlib.sha256(pass_salt.encode()).hexdigest()

        return hash, salt
    
    password_hash, password_salt = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash, password_salt) VALUES (?, ?, ?)", (username.lower(), password_hash, password_salt))
        connection.commit()
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False
    
def get_user_by_username(username):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username.lower(),))
    row = cursor.fetchone()
    if row is None:
        return None # no username found
    
    return dict(row)

def delete_user(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        connection.commit()
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False
