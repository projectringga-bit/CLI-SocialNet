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


def format_timestamp(timestamp):
    if timestamp is None:
        return "unknown time"
    
    date_time = datetime.datetime.fromtimestamp(timestamp)
    now = datetime.datetime.now()

    difference = now - date_time

    if difference.days == 0:
        if difference.seconds < 60:
            return "just now"
        
        elif difference.seconds < 3600:
            minutes = difference.seconds // 60
            return f"{minutes} minute(s) ago"
        
        else:
            hours = difference.seconds // 3600
            return f"{hours} hour(s) ago"
        
    elif difference.days == 1:
        return "yesterday"
    
    elif difference.days < 7:
        return f"{difference.days} day(s) ago"
    
    else:
        return date_time.strftime("%Y-%m-%d")


def print_post(data):
    post_id = data.get("id", "")
    username = data.get("username", "unknown")
    display_name = data.get("display_name", "")
    content = data.get("content", "")
    created_at = data.get("created", None)
    likes = data.get("like_count", 0)
    image_ascii = data.get("image_ascii", None)

    if display_name:
        name = f"{display_name} (@{username})"
    else:
        name = f"@{username}"

    print_separator()
    print(f"[{post_id}] {name} • {format_timestamp(created_at)}")
    print(f"    {content}")

    if image_ascii:
        print("")
        for line in image_ascii.split("\n"):
            print(f"    {line}")
        print("")
        
    print(f"    ❤️  {likes} Likes")


def print_profile(user):
    username = user.get("username", "unknown")
    display_name = user.get("display_name", "")
    bio = user.get("bio", "No bio")
    status = user.get("status", "")
    location = user.get("location", "")
    website = user.get("website", "")
    created = user.get("created", None)
    followers_count = user.get("followers_count", 0)
    following_count = user.get("following_count", 0)
    posts_count = user.get("posts_count", 0)
    profile_ascii = user.get("profile_ascii", None)
    is_admin = user.get("is_admin", 0)
    is_verified = user.get("is_verified", 0)
    is_private = user.get("is_private", 0)

    print_separator()

    if profile_ascii:
        for line in profile_ascii.split("\n"):
            print(f"    {line}")
        print()

    if display_name:
        print(f"@{username} ({display_name})")

    else:
        print(f"@{username}")

    if is_admin:
        print("  🛡️  Admin")
    
    if is_verified:
        print("   ✓  Verified")

    if is_private:
        print("  🔒  Private Account")

    if status:
        print(f"  💭 Status: {status}")
    
    print(f"  📝 Bio: {bio}")

    if location:
        print(f"  📍 Location: {location}")

    if website:
        print(f"  🔗 Website: {website}")

    print(f"\n  {posts_count} Posts • {followers_count} Followers • {following_count} Following")
    print(f"  Joined: {format_timestamp(created)}")
    
    print_separator()


def print_comment(data):
    comment_id = data.get("id", "")
    username = data.get("username", "unknown")
    display_name = data.get("display_name", "")
    content = data.get("content", "")
    created = data.get("created", None)

    if display_name:
        name = f"{display_name} (@{username})"
    else:
        name = f"@{username}"

    print(f"  [{comment_id}] {name}")
    print(f"    {content}")
    print(f"    • {format_timestamp(created)}")  
