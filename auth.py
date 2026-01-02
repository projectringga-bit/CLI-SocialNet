import re
import hashlib
import secrets

import db


current_user = None


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(32)
            
    pass_salt = password + salt
    hash = hashlib.sha256(pass_salt.encode()).hexdigest()

    return hash, salt
        
def verify_password(password, hashed_password, salt):
    new_hash, _ = hash_password(password, salt)
    if new_hash == hashed_password:
        return True
    
    return False


def get_current_user():
    global current_user
    return current_user


def is_logged():
    return current_user is not None


def register(username, password):
    if not username:
        return False, "Username cannot be empty."

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if len(username) > 20:
        return False, "Username cannot be longer than 20 characters."

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."

    if not password:
        return False, "Password cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    if db.create_user(username, password):
        return True, "User registered successfully."
    else:
        return False, "Username is already taken."


def login(username, password):
    global current_user
    user = db.get_user_by_username(username)

    if user is None:
        return False
    
    if verify_password(password, user["password_hash"], user["password_salt"]):
        current_user = user
        return True
    else:
        return False


def logout():
    global current_user
    current_user = None
    return True


def delete_account(password):
    global current_user

    if not is_logged():
        return False
    
    if not verify_password(password, current_user["password_hash"], current_user["password_salt"]):
        return False

    db.delete_user(current_user["id"])

    logout()

    return True
