from pymongo import MongoClient
from pymongo import DESCENDING
from pymongo import ReturnDocument

from utils import hash_password, timestamp
from config import MONGODB_URI, MONGODB_NAME
from config import DEFAULT_ADMIN_PASSWORD

mongo_client = None
mongo_database = None

def connect_db():
    global mongo_client, mongo_database
    
    if mongo_client is None:
        mongo_client = MongoClient(MONGODB_URI)
        mongo_database = mongo_client[MONGODB_NAME]

    return mongo_database

def close_db():
    global mongo_client, mongo_database
    
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        mongo_database = None

def init_db():
    db = connect_db()

    counters = db["counters"]

    users = db["users"]
    users.create_index("username", unique=True)

    registration_limits = db["registration_limits"]
    registration_limits.create_index("machine_id")

    sessions = db["sessions"]
    sessions.create_index("token", unique=True)
    sessions.create_index("user_id")
    sessions.create_index("expires")

    posts = db["posts"]
    posts.create_index("user_id")
    posts.create_index("created")

    reposts = db["reposts"]
    reposts.create_index("user_id")
    reposts.create_index("post_id")

    bookmarks = db["bookmarks"]
    bookmarks.create_index("user_id", unique=True)
    bookmarks.create_index("post_id", unique=True)

    pinned_posts = db["pinned_posts"]
    pinned_posts.create_index("user_id", unique=True)
    pinned_posts.create_index("post_id", unique=True)

    hashtags = db["hashtags"]
    hashtags.create_index("hashtag", unique=True)

    post_hashtags = db["post_hashtags"]
    post_hashtags.create_index("post_id", unique=True)
    post_hashtags.create_index("hashtag_id", unique=True)

    mentions = db["mentions"]
    mentions.create_index("post_id", unique=True)
    mentions.create_index("mentioned_user", unique=True)

    likes = db["likes"]
    likes.create_index("user_id", unique=True)
    likes.create_index("post_id", unique=True)

    follows = db["follows"]
    follows.create_index("follower_id", unique=True)
    follows.create_index("followed_id", unique=True)

    comments = db["comments"]
    comments.create_index("user_id")
    comments.create_index("post_id")

    messages = db["messages"]
    messages.create_index("sender_id")
    messages.create_index("receiver_id")

    closed_conversations = db["closed_conversations"]
    closed_conversations.create_index("user_id", unique=True)
    closed_conversations.create_index("other_user_id", unique=True)

    notifications = db["notifications"]
    notifications.create_index("user_id")
    
    admin_logs = db["admin_logs"]
    admin_logs.create_index("admin_id")
    admin_logs.create_index("target_user_id")

    command_aliases = db["command_aliases"]
    command_aliases.create_index("user_id", unique=True)
    command_aliases.create_index("alias", unique=True)

    return True


def get_next_id(name):
    db = connect_db()
    counters = db["counters"]

    result = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    return result["seq"]


def can_view_content(viewer_id, content_owner_id):
    db = connect_db()
    users = db["users"]
    follows = db["follows"]

    if viewer_id == content_owner_id:
        return True
    
    owner = users.find_one({"_id": content_owner_id})
    if owner is None:
        return False
    
    if owner.get("is_private", 0) == 0:
        return True
    
    viewer_follows_the_owner = follows.find_one({
        "follower_id": viewer_id,
        "followed_id": content_owner_id
    })

    owner_follows_the_viewer = follows.find_one({
        "follower_id": content_owner_id,
        "followed_id": viewer_id
    })

    if viewer_follows_the_owner and owner_follows_the_viewer:
        return True
    
    return False


def create_user(username, password, machine_id=None):
    db = connect_db()
    users = db["users"]
    registration_limits = db["registration_limits"]

    now_timestamp = timestamp()

    if machine_id is not None:
        hour = now_timestamp - 3600

        count = registration_limits.count_documents({
            "machine_id": machine_id,
            "created_at": {"$gte": hour}
        })
        if count >= 3:
            return False, "Registration limit exceeded for this machine. Please try again later."
        
    existing = users.find_one({"username": username.lower()})
    if existing:
        return False, "Username is already taken."

    password_hash, password_salt = hash_password(password)

    try:
        user_id = get_next_id("user_id")

        users.insert_one({
            "_id": user_id,
            "username": username.lower(),
            "password_hash": password_hash,
            "password_salt": password_salt,
            "created": now_timestamp,
            "display_name": "",
            "bio": "",
            "status": "",
            "location": "",
            "website": "",
            "profile_ascii": "",
            "is_admin": 0,
            "is_banned": 0,
            "ban_reason": "",
            "is_private": 0,
            "is_verified": 0,
            "login_attempts": 0,
            "locked_until": 0,
        })

        if machine_id is not None:
            registration_limits.insert_one({
                "machine_id": machine_id,
                "username": username.lower(),
                "created": now_timestamp
            })

        return True, "User created successfully."
    
    except Exception as e:
        return False, f"Error: {e}"

def get_user_by_username(username):
    db = connect_db()
    users = db["users"]
    
    user = users.find_one({"username": username.lower()})
    if user is None:
        return None
    
    user["id"] = user["_id"]

    return dict(user)

def get_user_by_id(user_id):
    db = connect_db()
    users = db["users"]
    
    user = users.find_one({"_id": user_id})
    if user is None:
        return None
    
    user["id"] = user["_id"]

    return dict(user)

def delete_user(user_id):
    db = connect_db()
    users = db["users"]
    
    try:
        users.delete_one({"_id": user_id})
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def change_user_password(user_id, new_password):
    db = connect_db()
    users = db["users"]
    
    new_password_hash, new_password_salt = hash_password(new_password)

    try:
        users.update_one(
            {"_id": user_id},
            {"$set": {
                "password_hash": new_password_hash,
                "password_salt": new_password_salt
            }}
        )
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def create_session(user_id, token, expires):
    db = connect_db()
    sessions = db["sessions"]
    
    now_timestamp = timestamp()

    try:
        sessions.insert_one({
            "user_id": user_id,
            "token": token,
            "created": now_timestamp,
            "expires": expires
        })
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def get_session(token):
    db = connect_db()
    sessions = db["sessions"]
    
    session = sessions.find_one({"token": token})
    if session is None:
        return None
    
    session["id"] = session["_id"]

    return dict(session)

def delete_session(token):
    db = connect_db()
    sessions = db["sessions"]
    
    try:
        sessions.delete_one({"token": token})
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def delete_user_sessions(user_id):
    db = connect_db()
    sessions = db["sessions"]
    
    try:
        sessions.delete_many({"user_id": user_id})
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def clean_expired_sessions():
    db = connect_db()
    sessions = db["sessions"]

    now_timestamp = timestamp()

    try:
        sessions.delete_many({"expires": {"$lt": now_timestamp}})
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def create_post(user_id, content, image_ascii=None):
    db = connect_db()
    posts = db["posts"]
    
    now_timestamp = timestamp()

    last = posts.find_one({
        "user_id": user_id,
        "deleted": 0
        },
        sort= [("created", DESCENDING)]
    )

    if last:
        time_since_last = now_timestamp - last["created"]
        if time_since_last < 5:
            wait = 5 - time_since_last
            return False, f"You are posting too quickly. Please wait {wait} seconds."
        
    try:
        post_id = get_next_id("post_id")

        result = posts.insert_one({
            "_id": post_id,
            "user_id": user_id,
            "content": content,
            "image_ascii": image_ascii,
            "created": now_timestamp,
            "deleted": 0
        })

        post_id = result.inserted_id

        return True, post_id
    
    except Exception as e:
        return False, f"Error: {e}"
    
def get_post(post_id, viewer_id=None):
    db = connect_db()
    posts = db["posts"]
    users = db["users"]
    likes = db["likes"]
    comments = db["comments"]
    reposts = db["reposts"]

    post = posts.find_one({"_id": post_id,
                            "deleted": 0
                            })
    if post is None:
        return None
    
    user = users.find_one({"_id": post["user_id"]})
    if user is None:
        return None
    
    post["like_count"] = likes.count_documents({"post_id": post_id})
    post["comment_count"] = comments.count_documents({"post_id": post_id, "deleted": 0})
    post["repost_count"] = reposts.count_documents({"post_id": post_id, "is_deleted": 0})

    post["id"] = post["_id"]

    if viewer_id is not None:
        if not can_view_content(viewer_id, post["user_id"]):
            return None
        
    return dict(post)

def delete_post(post_id):
    db = connect_db()
    posts = db["posts"]
    
    try:
        posts.update_one(
            {"_id": post_id},
            {"$set": {"deleted": 1}}
        )
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def get_feed_posts(user_id, limit=20, offset=0):
    db = connect_db()
    posts = db["posts"]
    users = db["users"]
    follows = db["follows"]
    likes = db["likes"]
    comments = db["comments"]
    reposts = db["reposts"]

    following = follows.find({"follower_id": user_id})

    following_ids =  []
    for f in following:
        following_ids.append(f["followed_id"])
    following_ids.append(user_id)

    results = []

    cursor = posts.find({
        "user_id": {"$in": following_ids},
        "deleted": 0
    }).sort("created", DESCENDING)

    for post in cursor:
        if post["user_id"] == user_id:
            include_post = True
        
        else:
            user = users.find_one({"_id": post["user_id"]})
            if user and user.get("is_private", 0) == 1:
                include_post = True

            else:
                is_mutual = follows.find_one({
                    "follower_id": user_id,
                    "followed_id": post["user_id"]
                }) and follows.find_one({
                    "follower_id": post["user_id"],
                    "followed_id": user_id
                })

                include_post = is_mutual

        if include_post:
            user = users.find_one({"_id": post["user_id"]})

            if user:
                post["username"] = user["username"]
            
            post["like_count"] = likes.count_documents({"post_id": post["_id"]})
            post["comment_count"] = comments.count_documents({"post_id": post["_id"], "deleted": 0})
            post["repost_count"] = reposts.count_documents({"post_id": post["_id"], "is_deleted": 0})

            post["id"] = post["_id"]
            
            results.append(dict(post))

            if len(results) >= limit + offset:
                break

    return results[offset:offset + limit]

def get_posts_by_id(user_id, limit=10, offset=0, viewer_id=None):
    db = connect_db()
    posts = db["posts"]
    users = db["users"]
    likes = db["likes"]
    comments = db["comments"]
    reposts = db["reposts"]

    if viewer_id is not None:
        if not can_view_content(viewer_id, user_id):
            return []
        
    results = []

    posts = posts.find({"user_id": user_id,
                        "deleted": 0
                        })
    
    for post in posts.sort("created", DESCENDING):
        user = users.find_one({"_id": post["user_id"]})

        if user:
            post["username"] = user["username"]
        
        post["like_count"] = likes.count_documents({"post_id": post["_id"]})
        post["comment_count"] = comments.count_documents({"post_id": post["_id"], "deleted": 0})
        post["repost_count"] = reposts.count_documents({"post_id": post["_id"], "is_deleted": 0})
        post["repost_id"] = None
        post["repost_username"] = None
        post["quote_content"] = None
        post["original_created"] = post["created"]
        
        post["id"] = post["_id"]

        results.append(dict(post))

    reposts = reposts.find({"user_id": user_id,
                            "is_deleted": 0
                            })
    
    for repost in reposts.sort("created", DESCENDING):
        post = posts.find_one({"_id": repost["post_id"],
                                "deleted": 0
                                })
        if post:
            post_user = users.find_one({"_id": post["user_id"]})
            repost_user = users.find_one({"_id": repost["user_id"]})

            if post_user:
                post["username"] = post_user["username"]

            post["like_count"] = likes.count_documents({"post_id": post["_id"]})
            post["comment_count"] = comments.count_documents({"post_id": post["_id"], "deleted": 0})
            post["repost_count"] = reposts.count_documents({"post_id": post["_id"], "is_deleted": 0})
            post["repost_id"] = repost["_id"]
            if repost_user:
                post["repost_username"] = repost_user["username"]
            post["quote_content"] = repost.get("quote_content", None)
            post["original_created"] = post["created"]

            post["id"] = post["_id"]

            results.append(dict(post))

    results.sort(key=lambda x: x.get("original_created"), reverse=True)

    return results[offset:offset + limit]

def get_post_owner(post_id):
    db = connect_db()
    posts = db["posts"]
    
    post = posts.find_one({"_id": post_id})
    if post is None:
        return None
    
    return post["user_id"]

def like_post(user_id, post_id):
    db = connect_db()
    likes = db["likes"]

    owner = get_post_owner(post_id)
    if not can_view_content(user_id, owner):
        return False, "You cannot like this post."
    
    existing = likes.find_one({
        "user_id": user_id,
        "post_id": post_id
    })
    if existing:
        return False, "You have already liked this post."

    now_timestamp = timestamp()

    try:
        likes.insert_one({
            "user_id": user_id,
            "post_id": post_id,
            "created": now_timestamp
        })

        return True, 1
    
    except Exception as e:
        return False, f"Error: {e}"

def get_unread_notifications_count(user_id):
    db = connect_db()
    notifications = db["notifications"]

    count = notifications.count_documents({
        "user_id": user_id,
        "is_read": 0
    })

    return count

def get_unread_messages_count(user_id):
    db = connect_db()
    messages = db["messages"]

    count = messages.count_documents({
        "receiver_id": user_id,
        "is_read": 0
    })

    return count

def get_user_aliases(user_id):
    db = connect_db()
    command_aliases = db["command_aliases"]

    results = {}
    aliases = command_aliases.find({"user_id": user_id})

    for alias in aliases:
        results[alias["alias"]] = alias["command"]

    return results

def update_user(user_id, **kwargs):
    db = connect_db()
    users = db["users"]

    allowed_fields = ["display_name", "bio", "status", "location", "website", "profile_ascii", "is_banned", "ban_reason", "is_admin", "is_verified", "is_private", "login_attempts", "locked_until"]

    updates = {}
    for field, value in kwargs.items():
        if field in allowed_fields:
            updates[field] = value

    if not updates:
        return False
    
    try:
        users.update_one(
            {"_id": user_id},
            {"$set": updates}
        )
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
