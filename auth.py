import re
import hashlib
import secrets

import db
from utils import verify_password, validate_username, validate_password


current_user = None


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
    global current_user
    user = db.get_user_by_username(username)

    if user is None:
        return False, "Warning: User not found."
    
    if verify_password(password, user["password_hash"], user["password_salt"]):
        current_user = user
        return True, f"Welcome back, @{username}!"
    
    else:
        return False, "Error: Wrong password."


def logout():
    global current_user
    current_user = None
    return True, "You have been logged out."


def delete_account(password):
    global current_user

    if not is_logged():
        return False, "Warning: No user is currently logged in."
    
    if not verify_password(password, current_user["password_hash"], current_user["password_salt"]):
        return False, "Error: Incorrect password. Account deletion aborted."

    db.delete_user(current_user["id"])

    logout()

    return True, "Your account has been deleted."


def change_password(old_password, new_password):
    global current_user

    if not is_logged():
        return False, "Warning: No user is currently logged in."
    
    if not verify_password(old_password, current_user["password_hash"], current_user["password_salt"]):
        return False, "Error: Current password is incorrect."
    
    valid, error = validate_password(new_password)
    if not valid:
        return False, error
    
    db.change_user_password(current_user["id"], new_password)

    return True, "Password changed successfully."
