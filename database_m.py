from pymongo import MongoClient
from pymongo import DESCENDING, ASCENDING
from pymongo import ReturnDocument
import re

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
    posts.create_index([("deleted", ASCENDING), ("created", DESCENDING)])

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
    likes.create_index([("user_id", ASCENDING), ("post_id", ASCENDING)], unique=True)

    follows = db["follows"]
    follows.create_index([("follower_id", ASCENDING), ("followed_id", ASCENDING)], unique=True)

    comments = db["comments"]
    comments.create_index("user_id")
    comments.create_index("post_id")

    messages = db["messages"]
    messages.create_index("sender_id")
    messages.create_index("receiver_id")
    messages.create_index([("receiver_id", ASCENDING), ("is_read", ASCENDING)])

    closed_conversations = db["closed_conversations"]
    closed_conversations.create_index([("user_id", ASCENDING), ("other_user_id", ASCENDING)], unique=True)

    notifications = db["notifications"]
    notifications.create_index("user_id")
    notifications.create_index([("user_id", ASCENDING), ("is_read", ASCENDING)])
    
    admin_logs = db["admin_logs"]
    admin_logs.create_index("admin_id")
    admin_logs.create_index("target_user_id")

    command_aliases = db["command_aliases"]
    command_aliases.create_index([("user_id", ASCENDING), ("alias", ASCENDING)], unique=True)

    create_admin()

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
            "created": {"$gte": hour}
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
        session_id = get_next_id("session_id")

        sessions.insert_one({
            "_id": session_id,
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

    post = posts.find_one({
        "_id": post_id,
        "deleted": 0
    })
    if post is None:
        return None
    
    user = users.find_one({"_id": post["user_id"]})
    if user:
        post["username"] = user["username"]
    
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
            if user and user.get("is_private", 0) == 0:
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

def get_global_feed_posts(limit=10, offset=0, viewer_id=None):
    db = connect_db()
    posts = db["posts"]
    users = db["users"]
    likes = db["likes"]
    comments = db["comments"]
    reposts = db["reposts"]
    follows = db["follows"]

    results = []

    if viewer_id is None: # only public
        cursor = posts.find({
            "deleted": 0
        }).sort("created", DESCENDING)

        for post in cursor:
            user = users.find_one({"_id": post["user_id"]})

            if user:
                if user.get("is_private", 0) == 0:
                    post["username"] = user["username"]
                    post["like_count"] = likes.count_documents({"post_id": post["_id"]})
                    post["comment_count"] = comments.count_documents({"post_id": post["_id"], "deleted": 0})
                    post["repost_count"] = reposts.count_documents({"post_id": post["_id"], "is_deleted": 0})

                    post["id"] = post["_id"]

                    results.append(dict(post))

            if len(results) >= limit + offset:
                break

    else:
        cursor = posts.find({
            "deleted": 0
        }).sort("created", DESCENDING)

        for post in cursor:
            if post["user_id"] == viewer_id:
                include_post = True
            
            else:
                user = users.find_one({"_id": post["user_id"]})
                if user and user.get("is_private", 0) == 0:
                    include_post = True

                else:
                    is_mutual = follows.find_one({
                        "follower_id": viewer_id,
                        "followed_id": post["user_id"]
                    }) and follows.find_one({
                        "follower_id": post["user_id"],
                        "followed_id": viewer_id
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

    posts = posts.find({
        "user_id": user_id,
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

    reposts = reposts.find({
        "user_id": user_id,
        "is_deleted": 0
        })
    
    for repost in reposts.sort("created", DESCENDING):
        post = posts.find_one({
            "_id": repost["post_id"],
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
        result = likes.insert_one({
            "user_id": user_id,
            "post_id": post_id,
            "created": now_timestamp
        })

        owner = get_post_owner(post_id)
        if owner != user_id:
            user = get_user_by_id(user_id)
            create_notification(owner, "like", f"User @{user['username']} liked your #{post_id} post.")


        return True, result.inserted_id
    
    except Exception as e:
        return False, f"Error: {e}"

def unlike_post(user_id, post_id):
    db = connect_db()
    likes = db["likes"]

    existing = likes.find_one({
        "user_id": user_id,
        "post_id": post_id
    })
    if existing is None:
        return False, "You have not liked this post."
    
    try:
        likes.delete_one({
            "user_id": user_id,
            "post_id": post_id
        })
        return True, existing["_id"]
    
    except Exception as e:
        return False, f"Error: {e}"
    
def get_post_likes(post_id):
    db = connect_db()
    likes = db["likes"]
    users = db["users"]

    results = []

    cursor = likes.find({"post_id": post_id}).sort("created", DESCENDING)

    for like in cursor:
        user = users.find_one({"_id": like["user_id"]})
        if user:
            results.append({
                "id": user["_id"],
                "username": user["username"]
            })

    return results

def get_posts_count(user_id):
    db = connect_db()
    posts = db["posts"]

    count = posts.count_documents({
        "user_id": user_id,
        "deleted": 0
    })

    return count

def follow_user(current_user_id, target_user_id):
    db = connect_db()
    follows = db["follows"]

    if current_user_id == target_user_id:
        return False, "You cannot follow yourself."
    
    existing = follows.find_one({
        "follower_id": current_user_id,
        "followed_id": target_user_id
    })
    if existing:
        return False, "You are already following this user."
    
    now_timestamp = timestamp()

    try:
        result = follows.insert_one({
            "follower_id": current_user_id,
            "followed_id": target_user_id,
            "created": now_timestamp
        })

        follower = get_user_by_id(current_user_id)
        create_notification(target_user_id, "follow", f"User @{follower['username']} started following you.")

        return True, result.inserted_id

    except Exception as e:
        return False, f"Error: {e}"

def unfollow_user(current_user_id, target_user_id):
    db = connect_db()
    follows = db["follows"]

    existing = follows.find_one({
        "follower_id": current_user_id,
        "followed_id": target_user_id
    })
    if existing is None:
        return False, "You are not following this user."
    
    try:
        follows.delete_one({
            "follower_id": current_user_id,
            "followed_id": target_user_id
        })
        return True, existing["_id"]
    
    except Exception as e:
        return False, f"Error: {e}"
    
def get_followers(user_id):
    db = connect_db()
    follows = db["follows"]
    users = db["users"]

    results = []

    cursor = follows.find({"followed_id": user_id}).sort("created", DESCENDING)

    for follow in cursor:
        user = users.find_one({"_id": follow["follower_id"]})
        if user:
            results.append({
                "id": user["_id"],
                "username": user["username"]
            })

    return results

def get_following(user_id, viewer_id=None):
    db = connect_db()
    follows = db["follows"]
    users = db["users"]

    if viewer_id is not None:
        if not can_view_content(viewer_id, user_id):
            return []

    results = []

    cursor = follows.find({"follower_id": user_id}).sort("created", DESCENDING)

    for follow in cursor:
        user = users.find_one({"_id": follow["followed_id"]})
        if user:
            results.append({
                "id": user["_id"],
                "username": user["username"]
            })

    return results

def get_followers_count(user_id):
    db = connect_db()
    follows = db["follows"]

    count = follows.count_documents({
        "followed_id": user_id
    })

    return count

def get_following_count(user_id, viewer_id=None):
    db = connect_db()
    follows = db["follows"]

    if viewer_id is not None:
        if not can_view_content(viewer_id, user_id):
            return 0

    count = follows.count_documents({
        "follower_id": user_id
    })

    return count

def is_following(follower_id, followed_id):
    db = connect_db()
    follows = db["follows"]

    existing = follows.find_one({
        "follower_id": follower_id,
        "followed_id": followed_id
    })
    if existing:
        return True
    
    return False

def create_comment(user_id, post_id, content):
    db = connect_db()
    comments = db["comments"]

    owner = get_post_owner(post_id)
    if not can_view_content(user_id, owner):
        return False, "You cannot comment on this post."
    
    now_timestamp = timestamp()

    try:
        comment_id = get_next_id("comment_id")

        result = comments.insert_one({
            "_id": comment_id,
            "user_id": user_id,
            "post_id": post_id,
            "content": content,
            "created": now_timestamp,
            "deleted": 0
        })

        owner = get_post_owner(post_id)
        if owner != user_id:
            user = get_user_by_id(user_id)
            create_notification(owner, "comment", f"User @{user['username']} commented on your #{post_id} post.")
        
        return True, comment_id
    
    except Exception as e:
        return False, f"Error: {e}"

def get_comments_by_post(post_id, limit, viewer_id=None):
    db = connect_db()
    comments = db["comments"]
    users = db["users"]

    if viewer_id is not None:
        owner = get_post_owner(post_id)
        if not can_view_content(viewer_id, owner):
            return []
        
    results = []

    cursor = comments.find({
        "post_id": post_id,
        "deleted": 0
    }).sort("created", DESCENDING).limit(limit)

    for comment in cursor:
        user = users.find_one({"_id": comment["user_id"]})
        if user:
            comment["username"] = user["username"]
        
        comment["id"] = comment["_id"]

        results.append(dict(comment))

    return results

def get_comments_count(post_id):
    db = connect_db()
    comments = db["comments"]

    count = comments.count_documents({
        "post_id": post_id,
        "deleted": 0
    })

    return count

def get_comment(comment_id):
    db = connect_db()
    comments = db["comments"]
    users = db["users"]

    comment = comments.find_one({
        "_id": comment_id,
        "deleted": 0
    })
    if comment is None:
        return None
    
    user = users.find_one({"_id": comment["user_id"]})
    if user:
        comment["username"] = user["username"]

    comment["id"] = comment["_id"]

    return dict(comment)

def delete_comment(comment_id):
    db = connect_db()
    comments = db["comments"]
    
    try:
        comments.update_one(
            {"_id": comment_id},
            {"$set": {"deleted": 1}}
        )
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def create_repost(user_id, post_id, content=None):
    db = connect_db()
    reposts = db["reposts"]

    owner = get_post_owner(post_id)
    if not can_view_content(user_id, owner):
        return False, "You cannot repost this post."
    
    existing = reposts.find_one({
        "user_id": user_id,
        "post_id": post_id,
        "is_deleted": 0
    })
    if existing:
        return False, "You have already reposted this post."
    
    now_timestamp = timestamp()

    try:
        result = reposts.insert_one({
            "user_id": user_id,
            "post_id": post_id,
            "content": content,
            "created": now_timestamp,
            "is_deleted": 0
        })

        owner = get_post_owner(post_id)
        if owner != user_id:
            user = get_user_by_id(user_id)
            if content:
                create_notification(owner, "quote_repost", f"User @{user['username']} quote reposted your #{post_id} post.")
            else:
                create_notification(owner, "repost", f"User @{user['username']} reposted your #{post_id} post.")
   
        return True, result.inserted_id
    
    except Exception as e:
        return False, f"Error: {e}"
    
def delete_repost(repost_id):
    db = connect_db()
    reposts = db["reposts"]
    
    repost = reposts.find_one({
        "user_id": repost_id,
        "post_id": repost_id,
        "is_deleted": 0
    })
    if repost is None:
        return False, "You have not reposted this post."
    
    try:
        reposts.update_one(
            {"post_id": repost_id,
             "user_id": repost_id},
            {"$set": {"is_deleted": 1}}
        )
        return True, repost["_id"]
    
    except Exception as e:
        return False, f"Error: {e}"
    
def get_reposts_count(post_id):
    db = connect_db()
    reposts = db["reposts"]

    count = reposts.count_documents({
        "post_id": post_id,
        "is_deleted": 0
    })

    return count

def get_reposts(post_id, viewer_id=None):
    db = connect_db()
    reposts = db["reposts"]
    users = db["users"]

    if viewer_id is not None:
        owner = get_post_owner(post_id)
        if not can_view_content(viewer_id, owner):
            return []
        
    results = []

    cursor = reposts.find({
        "post_id": post_id,
        "is_deleted": 0
    }).sort("created", DESCENDING)

    for repost in cursor:
        user = users.find_one({"_id": repost["user_id"]})
        if user:
            repost["username"] = user["username"]
        
        repost["id"] = repost["_id"]

        results.append(dict(repost))

    return results

def search_posts(query, limit=10, offset=0, viewer_id=None):
    db = connect_db()
    posts = db["posts"]
    users = db["users"]
    likes = db["likes"]
    comments = db["comments"]
    reposts = db["reposts"]
    follows = db["follows"]

    search_query = query.lower()
    search_query = re.escape(search_query)

    results = []

    cursor = posts.find({
        "content": {
            "$regex": search_query,
            "$options": "i"
        },
        "deleted": 0
    }).sort("created", DESCENDING)

    for post in cursor:
        if post["user_id"] == viewer_id:
            include_post = True
        
        else:
            user = users.find_one({"_id": post["user_id"]})
            if user and user.get("is_private", 0) == 0:
                include_post = True

            else:
                is_mutual = follows.find_one({
                    "follower_id": viewer_id,
                    "followed_id": post["user_id"]
                }) and follows.find_one({
                    "follower_id": post["user_id"],
                    "followed_id": viewer_id
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

def search_users(query, limit=10, offset=0):
    db = connect_db()
    users = db["users"]

    search_query = query.lower()
    search_query = re.escape(search_query)

    results = []

    cursor = users.find({
        "username": {
            "$regex": search_query,
            "$options": "i"
        },
        "is_banned": 0
    }).sort("created", DESCENDING).skip(offset).limit(limit)

    for user in cursor:
        user["id"] = user["_id"]
        results.append(dict(user))

    return results

def send_message(sender_id, receiver_id, content):
    db = connect_db()
    messages = db["messages"]

    now_timestamp = timestamp()

    try:
        result = messages.insert_one({
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content,
            "is_read": 0,
            "created": now_timestamp
        })

        reopen_conversation(receiver_id, sender_id)
        reopen_conversation(sender_id, receiver_id)

        sender = get_user_by_id(sender_id)
        create_notification(receiver_id, "message", f"New message from @{sender['username']}")

        return True, result.inserted_id
    
    except Exception as e:
        return False, f"Error: {e}"
    
def get_messages(user_id, other_id, limit=20):
    db = connect_db()
    messages = db["messages"]
    users = db["users"]

    results = []

    cursor = messages.find({
        "$or": [
            {"sender_id": user_id, "receiver_id": other_id},
            {"sender_id": other_id, "receiver_id": user_id}
        ]
    }).sort("created", ASCENDING).limit(limit)

    for message in cursor:
        sender = users.find_one({"_id": message["sender_id"]})
        receiver = users.find_one({"_id": message["receiver_id"]})

        if sender:
            message["sender_username"] = sender["username"]
        if receiver:
            message["receiver_username"] = receiver["username"]

        message["id"] = message["_id"]

        results.append(dict(message))

    return results

def get_conversations(user_id):
    db = connect_db()
    messages = db["messages"]
    closed_conversations = db["closed_conversations"]

    results = []

    cursor = messages.aggregate([
        {"$match": {
            "$or": [
                {"sender_id": user_id},
                {"receiver_id": user_id}
            ]
        }},
        {"$sort": {"created": -1}},
        {"$group": {
            "_id": {
                "$cond": [
                    {"$eq": ["$sender_id", user_id]},
                    "$receiver_id",
                    "$sender_id"
                ]
            },
            "last_message": {"$first": "$content"},
            "timestamp": {"$first": "$created"},
        }}
    ])

    for conversation in cursor:
        other_id = conversation["_id"]

        is_closed = closed_conversations.find_one({
            "user_id": user_id,
            "other_user_id": other_id
        })
        if not is_closed:
            user = get_user_by_id(other_id)
            if user:
                results.append({
                    "user_id": other_id,
                    "username": user["username"],
                    "last_message": conversation["last_message"],
                    "timestamp": conversation["timestamp"]
                })

    return results

def close_conversation(user_id, other_id):
    db = connect_db()
    closed_conversations = db["closed_conversations"]

    now_timestamp = timestamp()

    try:
        existing = closed_conversations.find_one({
            "user_id": user_id,
            "other_user_id": other_id
        })
        if existing is not None:
            return False, "Conversation is already closed."
        
        result = closed_conversations.insert_one({
            "user_id": user_id,
            "other_user_id": other_id,
            "created": now_timestamp
        })
        return True, result.inserted_id
    
    except Exception as e:
        return False, f"Error: {e}"
    
def reopen_conversation(user_id, other_id):
    db = connect_db()
    closed_conversations = db["closed_conversations"]

    try:
        closed_conversations.delete_one({
            "user_id": user_id,
            "other_user_id": other_id
        })
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_notification(user_id, type, content):
    db = connect_db()
    notifications = db["notifications"]

    now_timestamp = timestamp()

    notifications.insert_one({
        "user_id": user_id,
        "type": type,
        "content": content,
        "is_read": 0,
        "created": now_timestamp
    })

def get_notifications(user_id, limit=20):
    db = connect_db()
    notifications = db["notifications"]

    results = []

    cursor = notifications.find({
        "user_id": user_id
    }).sort("created", DESCENDING).limit(limit)

    for notification in cursor:
        notification["id"] = notification["_id"]
        results.append(dict(notification))

    return results

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

def mark_notifications(user_id):
    db = connect_db()
    notifications = db["notifications"]

    try:
        notifications.update_many(
            {"user_id": user_id},
            {"$set": {"is_read": 1}}
        )
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def mark_messages(user_id, sender):
    db = connect_db()
    messages = db["messages"]

    try:
        messages.update_many(
            {"receiver_id": user_id, "sender_id": sender},
            {"$set": {"is_read": 1}}
        )
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def clear_notifications(user_id):
    db = connect_db()
    notifications = db["notifications"]

    try:
        notifications.delete_many({"user_id": user_id})
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def create_alias(user_id, alias, command):
    db = connect_db()
    command_aliases = db["command_aliases"]

    now_timestamp = timestamp()

    try:
        existing = command_aliases.find_one({
            "user_id": user_id,
            "alias": alias
        })

        if existing:
            command_aliases.update_one({
                "user_id": user_id,
                "alias": alias
            },
            {"$set": {
                "command": command,
                "created": now_timestamp
            }})
            return True, f"Alias '{alias}' updated."
        
        else:
            command_aliases.insert_one({
                "user_id": user_id,
                "alias": alias,
                "command": command,
                "created": now_timestamp
            })
            return True, f"Alias '{alias}' created."
        
    except Exception as e:
        return False, f"Error: {e}"

def get_user_aliases(user_id):
    db = connect_db()
    command_aliases = db["command_aliases"]

    results = {}
    aliases = command_aliases.find({"user_id": user_id})

    for alias in aliases:
        results[alias["alias"]] = alias["command"]

    return results

def remove_alias(user_id, alias):
    db = connect_db()
    command_aliases = db["command_aliases"]

    try:
        command_aliases.delete_one({
            "user_id": user_id,
            "alias": alias
        })
        return True, f"Alias '{alias}' removed."

    except Exception as e:
        return False, f"Error: {e}"

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
    
def create_admin():
    db = connect_db()
    users = db["users"]

    admin = users.find_one({"is_admin": 1})
    
    if admin is None:
        password_hash, password_salt = hash_password(DEFAULT_ADMIN_PASSWORD)
        now_timestamp = timestamp()
        user_id = get_next_id("user_id")

        users.insert_one({
            "_id": user_id,
            "username": "admin",
            "password_hash": password_hash,
            "password_salt": password_salt,
            "created": now_timestamp,
            "display_name": "",
            "bio": "Admin",
            "status": "",
            "location": "",
            "website": "",
            "profile_ascii": "",
            "is_admin": 1,
            "is_banned": 0,
            "ban_reason": "",
            "is_private": 0,
            "is_verified": 1,
            "login_attempts": 0,
            "locked_until": 0
        })

def admin_log(admin_id, action, target_user_id=None, details=None):
    db = connect_db()
    admin_logs = db["admin_logs"]

    now_timestamp = timestamp()

    try:
        admin_logs.insert_one({
            "admin_id": admin_id,
            "action": action,
            "target_user_id": target_user_id,
            "details": details,
            "created": now_timestamp
        })
    
    except Exception as e:
        print(f"Error: {e}")

def get_admin_logs(limit, offset):
    db = connect_db()
    admin_logs = db["admin_logs"]
    users = db["users"]

    results = []

    cursor = admin_logs.find().sort("created", DESCENDING).skip(offset).limit(limit)

    for log in cursor:
        log["id"] = log["_id"]

        admin = users.find_one({"_id": log["admin_id"]})
        if admin:
            log["admin_username"] = admin["username"]

        results.append(dict(log))

    return results

def get_statistics():
    db = connect_db()
    users = db["users"]
    posts = db["posts"]
    comments = db["comments"]
    likes = db["likes"]
    reposts = db["reposts"]
    follows = db["follows"]

    stats = {}

    stats["user_count"] = users.count_documents({})
    stats["banned_count"] = users.count_documents({"is_banned": 1})
    stats["post_count"] = posts.count_documents({"deleted": 0})
    stats["like_count"] = likes.count_documents({})
    stats["follow_count"] = follows.count_documents({})
    stats["comment_count"] = comments.count_documents({"deleted": 0})
    stats["repost_count"] = reposts.count_documents({"is_deleted": 0})

    return stats
