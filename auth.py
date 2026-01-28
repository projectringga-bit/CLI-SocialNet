import hashlib
import socket
import uuid
import platform

import db
from config import ENABLE_REGISTRATION_LIMIT
from utils import verify_password, validate_username, validate_password, generate_token, timestamp


current_user = None
current_token = None


def get_current_user():
    global current_user
    return current_user


def is_logged():
    return current_user is not None


def is_admin():
    if current_user:
        if current_user.get("is_admin", 0) == 1:
            return True
    
    return False


def register(username, password):
    valid, error = validate_username(username)
    if not valid:
        return False, error
    
    valid, error = validate_password(password)
    if not valid:
        return False, error
    
    hostname = socket.gethostname()

    mac_int = uuid.getnode()
    mac_bytes = mac_int.to_bytes(6, byteorder='big')
    mac_parts = []
    for byte in mac_bytes:
        mac_parts.append(f"{byte:02x}")
    
    mac_address = ":".join(mac_parts)

    system = platform.system()

    identifier = f"{hostname}:{mac_address}:{system}"
    machine_id = hashlib.sha256(identifier.encode()).hexdigest()
    
    if ENABLE_REGISTRATION_LIMIT:
        success, result = db.create_user(username, password, machine_id=machine_id)
    else:
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
    
    if user.get("is_banned") == 1:
        reason = user.get("ban_reason")
        return False, f"Your account has been banned. Reason: {reason}"
    
    time = timestamp()

    if user["locked_until"] > time:
        remain = (user["locked_until"] - time) // 60
        return False, f"Your account is locked due to multiple failed login attempts. Please try again in {remain} minutes."
    
    if verify_password(password, user["password_hash"], user["password_salt"]):
        token = generate_token()
        expires = time + 86400
        db.create_session(user["id"], token, expires)

        current_user = user
        current_token = token

        db.update_user(user["id"], login_attempts=0)

        return True, f"Welcome back, @{username}!"
    
    else:
        attempts = user["login_attempts"] + 1

        if attempts >= 5:
            lock_duration = time + 15 * 60 # 15 minutes
            db.update_user(user["id"], login_attempts=0, locked_until=lock_duration)

            return False, "Too many failed login attempts. Your account has been locked for 15 minutes."
        
        else:
            db.update_user(user["id"], login_attempts=attempts)
            remaining_attempts = 5 - attempts

            return False, f"Incorrect password. You have {remaining_attempts} more attempt(s)."


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

    if not current_token:
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

    if current_user and current_user.get("is_banned") == 1:
        logout()
        return False

    return True
