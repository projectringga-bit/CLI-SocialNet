import db
import auth
import ascii
from utils import print_profile, print_separator, print_error, print_info
from utils import format_timestamp


def follow(username):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    target = db.get_user_by_username(username)

    if target is None:
        return False, "User not found."
    
    current_user = auth.get_current_user()

    return db.follow_user(current_user["id"], target["id"])


def unfollow(username):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    target = db.get_user_by_username(username)

    if target is None:
        return False, "User not found."
    
    current_user = auth.get_current_user()

    if db.unfollow_user(current_user["id"], target["id"]):
        return True, f"You have unfollowed @{username}."
    else:
        return False, "You are not following this user."
    

def get_followers(username):
    if username:
        user = db.get_user_by_username(username)

        if user is None:
            return False, "User not found."
        
    else:
        if not auth.is_logged():
            return False, "You must be logged in."
        
        user = auth.get_current_user()

    followers = db.get_followers(user["id"])
        
    return True, followers


def get_following(username):
    if username:
        user = db.get_user_by_username(username)

        if user is None:
            return False, "User not found."
        
    else:
        if not auth.is_logged():
            return False, "You must be logged in."
        
        user = auth.get_current_user()

    following = db.get_following(user["id"])

    return True, following


def get_profile(username):
    if username:
        user = db.get_user_by_username(username)

    else:
        if not auth.is_logged():
            return None
        
        user = auth.get_current_user()

    if user is None:
        return None
    
    profile = {
        "id": user["id"],
        "username": user["username"],
        "display_name": user["display_name"] or '',
        "bio": user["bio"] or 'No bio',
        "status": user["status"] or '',
        "location": user["location"] or '',
        "website": user["website"] or '',
        "created": user["created"],
        "followers_count": db.get_followers_count(user["id"]),
        "following_count": db.get_following_count(user["id"]),
        "posts_count": db.get_posts_count(user["id"]),
        "profile_ascii": user["profile_ascii"] or None,
        "is_admin": user["is_admin"],
        "is_verified": user["is_verified"] or 0,
        "is_private": user["is_private"] or 0
    }

    if auth.is_logged():
        if username:
            current_user = auth.get_current_user()
        
            if current_user["id"] != user["id"]:
                profile["is_following"] = db.is_following(current_user["id"], user["id"])
                profile["follows_you"] = db.is_following(user["id"], current_user["id"])

    return profile


def update_display_name(new_display_name):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if len(new_display_name) > 50:
        return False, "Display name cannot be longer than 50 characters."
    
    user = auth.get_current_user()
    db.update_user(user["id"], display_name=new_display_name)

    return True, "Display name changed successfully."


def update_bio(new_bio):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if len(new_bio) > 250:
        return False, "Bio must be less than 250 characters."
    
    user = auth.get_current_user()
    db.update_user(user["id"], bio=new_bio)
    
    return True, "Bio updated."


def update_status(new_status):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if len(new_status) > 100:
        return False, "Status must be less than 100 characters."
    
    user = auth.get_current_user()
    db.update_user(user["id"], status=new_status)

    return True, "Status updated."


def update_location(new_location):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if len(new_location) > 100:
        return False, "Location must be less than 100 characters."
    
    user = auth.get_current_user()
    db.update_user(user["id"], location=new_location)

    return True, "Location updated."


def update_website(new_website):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if len(new_website) > 100:
        return False, "Website must be less than 100 characters."
    
    user = auth.get_current_user()
    db.update_user(user["id"], website=new_website)

    return True, "Website updated."


def update_avatar(avatar_path=None, avatar_url=None):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if avatar_url is not None:
        success, result = ascii.image_url_to_ascii(avatar_url)
        if not success:
            return False, result
        
        avatar_ascii = result
        user = auth.get_current_user()
        db.update_user(user["id"], profile_ascii=avatar_ascii)

        return True, "Avatar updated."
    
    success, result = ascii.image_to_ascii(avatar_path)
    if not success:
        return False, result
    
    user = auth.get_current_user()
    db.update_user(user["id"], profile_ascii=result)

    return True, "Avatar updated."


def remove_avatar():
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    db.update_user(user["id"], profile_ascii='')

    return True, "Avatar removed."


def change_private_status():
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()

    if user["is_private"] == 0:
        db.update_user(user["id"], is_private=1)

        return True, "Your account is now private."
    
    elif user["is_private"] == 1:
        db.update_user(user["id"], is_private=0)

        return True, "Your account is now public."


def display_followers(username):
    success, followers = get_followers(username)

    if success:
        if username:
            target = username
        else:
            current_user = auth.get_current_user()
            target = current_user["username"]

        if not followers:
            return False, f"@{target} has no followers."

        follower_list = []
        for follower in followers:
            follower_list.append(f"@{follower['username']}")

        return True, follower_list
    
    else:
        return False, followers
    

def display_following(username):
    success, following = get_following(username)

    if success:
        if username:
            target = username
        else:
            current_user = auth.get_current_user()
            target = current_user["username"]
    
        if not following:
            return True, f"@{target} is not following anyone."
        
        following_list = []
        for user in following:
            following_list.append(f"@{user['username']}")

        return True, following_list
    
    else:
        return False, following
    

def display_profile(username):
    profile = get_profile(username)

    if profile is None:
        return False, "User not found."
    
    posts = db.get_posts_by_id(profile["id"], limit=15)
    
    print_profile(profile, posts=posts)

    return True, None


def get_conversations():
    if not auth.is_logged():
        return False, "You must be logged in."
    
    current_user = auth.get_current_user()
    conversations = db.get_conversations(current_user["id"])

    return True, conversations


def send_message(username, content):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    current_user = auth.get_current_user()
    target = db.get_user_by_username(username)

    if target is None:
        return False, "User not found."
    
    if target["is_banned"] == 1:
        return False, "Cannot send message to this user."
    
    content = content.strip()
    if not content:
        return False, "Message content cannot be empty."
    
    if len(content) > 1000:
        return False, "Message content cannot exceed 1000 characters."
    
    if current_user["id"] == target["id"]:
        return False, "You cannot send a message to yourself."
    
    db.send_message(current_user["id"], target["id"], content)

    return True, f"Message sent to @{username}."


def get_messages(username):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    current_user = auth.get_current_user()
    target = db.get_user_by_username(username)

    if target is None:
        return False, "User not found."
    
    messages = db.get_messages(current_user["id"], target["id"])

    return True, messages

def display_conversations():
    success, conversations = get_conversations()

    if not success:
        print_error(conversations)
        return
    
    if not conversations:
        print_info("You have no conversations.")
        return

    print("Your Conversations:")

    for conversation in conversations:
        username = conversation["username"]
        last_message = conversation["last_message"]
        timestamp = conversation["timestamp"]
        print(f"@{username} - Last message {format_timestamp(timestamp)}: {last_message}")

    print_separator()


def display_messages(username):
    success, messages = get_messages(username)

    if not success:
        print_error(messages)
        return
    
    if not messages:
        print_info(f"No messages with @{username}.")
        return
    
    current_user = auth.get_current_user()

    for message in messages:
        if message["sender_id"] == current_user["id"]:
            sender = "You"
        
        else:
            sender = f"@{username}"
        
        time = format_timestamp(message["created"])
        print(f" [{time}] {sender}: {message['content']}")

    print_separator()
