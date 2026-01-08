import db
import auth


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
        "created_at": user["created_at"],
        "followers_count": db.get_followers_count(user["id"]),
        "following_count": db.get_following_count(user["id"]),
        "posts_count": db.get_posts_count(user["id"]),
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
