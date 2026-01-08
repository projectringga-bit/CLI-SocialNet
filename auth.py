import re
import hashlib
import secrets

import db
from utils import verify_password, validate_username, validate_password, generate_token, timestamp


current_user = None
current_token = None


def get_current_user():
    global current_user
    return current_user


def is_logged():
    return current_user is not None


def register(username, password):
    valid, error = validate_username(username)
    if not valid:
        return False, error
    
    valid, error = validate_password(password)
    if not valid:
        return False, error
    
    success, result = db.create_user(username, password)

    if success:
        return True, result
    else:
        return False, result


def login(username, password):
    global current_user, current_token
    user = db.get_user_by_username(username)

    if user is None:
        return False, "User not found."
    
    time = timestamp()
    
    if verify_password(password, user["password_hash"], user["password_salt"]):
        token = generate_token()
        expires = time + 86400
        db.create_session(user["id"], token, expires)

        current_user = user
        current_token = token

        return True, f"Welcome back, @{username}!"
    
    else:
        return False, "Wrong password."


def logout():
    global current_user, current_token
    
    if current_token:
        db.delete_session(current_token)
    
    current_user = None
    current_token = None

    return True, "You have been logged out."


def delete_account(password):
    global current_user

    if not is_logged():
        return False, "No user is currently logged in."
    
    if not verify_password(password, current_user["password_hash"], current_user["password_salt"]):
        return False, "Incorrect password. Account deletion aborted."

    db.delete_user(current_user["id"])

    logout()

    return True, "Your account has been deleted."


def change_password(old_password, new_password):
    global current_user

    if not is_logged():
        return False, "No user is currently logged in."
    
    if not verify_password(old_password, current_user["password_hash"], current_user["password_salt"]):
        return False, "Current password is incorrect."
    
    valid, error = validate_password(new_password)
    if not valid:
        return False, error
    
    db.change_user_password(current_user["id"], new_password)

    db.delete_user_sessions(current_user["id"])

    login(current_user["username"], new_password)

    return True, "Password changed successfully."

def validate_session():
    global current_user, current_token

    if not current_token or current_token != current_token:
        return False
    
    session = db.get_session(current_token)

    if session is None:
        current_user = None
        current_token = None
        return False
    
    now_timestamp = timestamp()

    if session["expires"] < now_timestamp:
        db.delete_session(current_token)
        current_user = None
        current_token = None
        return False
    
    current_user = db.get_user_by_id(session["user_id"])

    return True
