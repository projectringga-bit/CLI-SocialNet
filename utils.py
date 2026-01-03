import hashlib
import secrets
import re
import os
import sys
import time
import datetime


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


def generate_token():
    token = secrets.token_hex(32)
    return token


def validate_username(username):
    if not username:
        return False, "Username cannot be empty."

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if len(username) > 20:
        return False, "Username cannot be longer than 20 characters."

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."

    return True, ""


def validate_password(password):
    if not password:
        return False, "Password cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    return True, ""


def print_success(message):
    print(f"\033[92m ✓ {message}\033[0m")  # green

def print_error(message):
    print(f"\033[91m ✗ {message}\033[0m")  # red

def print_warning(message):
    print(f"\033[93m ⚠ {message}\033[0m")  # yellow

def print_info(message):
    print(f"\033[94m i {message}\033[0m")  # blue

def print_separator():
    print("\033[90m" + "-" * 40 + "\033[0m")  # gray


def print_banner():
    banner = r"""
   ________    ____   _____            _       ___   __     __ 
  / ____/ /   /  _/  / ___/____  _____(_)___ _/ / | / /__  / /_
 / /   / /    / /    \__ \/ __ \/ ___/ / __ `/ /  |/ / _ \/ __/
/ /___/ /____/ /    ___/ / /_/ / /__/ / /_/ / / /|  /  __/ /_  
\____/_____/___/   /____/\____/\___/_/\__,_/_/_/ |_/\___/\__/  
 ______              _           __  ____         _      __  _  __    __                  __     
/_  __/__ ______ _  (_)__  ___ _/ / / __/__  ____(_)__ _/ / / |/ /__ / /__    _____  ____/ /__   
 / / / -_) __/  ' \/ / _ \/ _ `/ / _\ \/ _ \/ __/ / _ `/ / /    / -_) __/ |/|/ / _ \/ __/  '_/   
/_/  \__/_/ /_/_/_/_/_//_/\_,_/_/ /___/\___/\__/_/\_,_/_/ /_/|_/\__/\__/|__,__/\___/_/ /_/\_\    
                                                                                                 
    """
    print("\033[96m" + banner + "\033[0m")  # cyan


def clear():
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")


def timestamp():
    timestamp = int(time.time())
    return timestamp