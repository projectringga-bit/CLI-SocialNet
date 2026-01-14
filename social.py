import db
import auth
import ascii
from utils import print_profile


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
        "is_verified": user["is_verified"] or 0
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
    
    print_profile(profile)

    if profile.get("is_following") and profile.get("follows_you"):
        follow_status = "You and this user follow each other."
    
    elif profile.get("is_following"):
        follow_status = "You are following this user."

    elif profile.get("follows_you"):
        follow_status = "This user follows you."

    else:
        follow_status = None

    return True, follow_status
