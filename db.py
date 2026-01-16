import sqlite3
import os

from utils import hash_password, timestamp
from config import DEFAULT_ADMIN_PASSWORD


db_connection = None

def connect_db():
    global db_connection

    db_connection = sqlite3.connect("socialnet.db")
    db_connection.row_factory = sqlite3.Row

    return db_connection

def close_db():
    global db_connection
    if db_connection is not None:
        db_connection.close()
        db_connection = None

def init_db():
    connection = connect_db()
    cursor = connection.cursor()
    
    # users
    cursor.execute("CREATE TABLE IF NOT EXISTS users (" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                    "username TEXT UNIQUE NOT NULL," \
                    "password_hash TEXT NOT NULL," \
                    "password_salt TEXT NOT NULL," \
                    "created INTEGER NOT NULL," \
                    "display_name TEXT DEFAULT ''," \
                    "bio TEXT DEFAULT ''," \
                    "status TEXT DEFAULT ''," \
                    "location TEXT DEFAULT ''," \
                    "website TEXT DEFAULT ''," \
                    "profile_ascii TEXT DEFAULT ''," \
                    "is_admin INTEGER DEFAULT 0," \
                    "is_banned INTEGER DEFAULT 0," \
                    "ban_reason TEXT DEFAULT '', " \
                    "is_private INTEGER DEFAULT 0," \
                    "is_verified INTEGER DEFAULT 0)")
    
    # sessions
    cursor.execute("CREATE TABLE IF NOT EXISTS sessions (" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                    "user_id INTEGER NOT NULL," \
                    "token TEXT UNIQUE NOT NULL," \
                    "created INTEGER NOT NULL," \
                    "expires INTEGER NOT NULL," \
                    "FOREIGN KEY (user_id) REFERENCES users(id))" )
    
    # posts
    cursor.execute("CREATE TABLE IF NOT EXISTS posts (" \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                    "user_id INTEGER NOT NULL," \
                    "content TEXT NOT NULL," \
                    "image_ascii TEXT DEFAULT NULL," \
                    "created INTEGER NOT NULL," \
                    "deleted INTEGER DEFAULT 0," \
                    "FOREIGN KEY (user_id) REFERENCES users(id))")
    
    # likes
    cursor.execute("CREATE TABLE IF NOT EXISTS likes (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "user_id INTEGER NOT NULL," \
                   "post_id INTEGER NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (user_id) REFERENCES users(id)," \
                   "FOREIGN KEY (post_id) REFERENCES posts(id)," \
                   "UNIQUE(user_id, post_id))")
    
    # follows
    cursor.execute("CREATE TABLE IF NOT EXISTS follows (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "follower_id INTEGER NOT NULL," \
                   "followed_id INTEGER NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (follower_id) REFERENCES users(id)," \
                   "FOREIGN KEY (followed_id) REFERENCES users(id)," \
                   "UNIQUE(follower_id, followed_id))")
    
    # Comments table
    cursor.execute("CREATE TABLE IF NOT EXISTS comments (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "user_id INTEGER NOT NULL," \
                   "post_id INTEGER NOT NULL," \
                   "content TEXT NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "deleted INTEGER DEFAULT 0," \
                   "FOREIGN KEY (user_id) REFERENCES users(id)," \
                   "FOREIGN KEY (post_id) REFERENCES posts(id))")
    
    # Messages table
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "sender_id INTEGER NOT NULL," \
                   "receiver_id INTEGER NOT NULL," \
                   "content TEXT NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (sender_id) REFERENCES users(id)," \
                   "FOREIGN KEY (receiver_id) REFERENCES users(id))")
                   
    # admin logs
    cursor.execute("CREATE TABLE IF NOT EXISTS admin_logs (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "admin_id INTEGER NOT NULL," \
                   "action TEXT NOT NULL," \
                   "target_user_id INTEGER," \
                   "details TEXT," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (admin_id) REFERENCES users(id)," \
                   "FOREIGN KEY (target_user_id) REFERENCES users(id))")


    connection.commit()

    create_admin()

    return True


def create_user(username, password): #TODO: limit or email verification
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username.lower(),))
    if cursor.fetchone() is not None:
        return False, "Username is already taken."
    
    password_hash, password_salt = hash_password(password)

    now_timestamp = timestamp()
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash, password_salt, created) VALUES (?, ?, ?, ?)", (username.lower(), password_hash, password_salt, now_timestamp))
        connection.commit()
        return True, "User created successfully."

    except Exception as e:
        return False, f"Error: {e}"
    
def get_user_by_username(username):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username.lower(),))
    row = cursor.fetchone()
    if row is None:
        return None # no username found
    
    return dict(row)

def get_user_by_id(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    
    return dict(row)

def delete_user(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        connection.commit()
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False
    
def change_user_password(user_id, new_password):
    connection = connect_db()
    cursor = connection.cursor()

    new_password_hash, new_password_salt = hash_password(new_password)

    try:
        cursor.execute("UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?", (new_password_hash, new_password_salt, user_id))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def create_session(user_id, token, expires):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO sessions (user_id, token, created, expires) VALUES (?, ?, ?, ?)", (user_id, token, now_timestamp, expires))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def get_session(token):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM sessions WHERE token = ?", (token,))
    row = cursor.fetchone()
    if row is None:
        return None
    
    return dict(row)
    
def delete_session(token):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def delete_user_sessions(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def clean_expired_sessions():
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    try:
        cursor.execute("DELETE FROM sessions WHERE expires < ?", (now_timestamp,))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def create_post(user_id, content, image_ascii=None):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    cursor.execute("SELECT created FROM posts WHERE user_id = ? AND deleted = 0 ORDER BY created DESC LIMIT 1", (user_id,))
    
    last = cursor.fetchone()
    if last:
        time_since_last = now_timestamp - last["created"]
        if time_since_last < 5:
            wait = 5 - time_since_last
            return False, f"You are posting too quickly. Please wait {wait} seconds."

    try:
        cursor.execute("INSERT INTO posts (user_id, content, image_ascii, created) VALUES (?, ?, ?, ?)", (user_id, content, image_ascii, now_timestamp))
        connection.commit()
        return True, cursor.lastrowid
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def get_post(post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT posts.*, users.username, (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count FROM posts JOIN users ON posts.user_id = users.id WHERE posts.id = ? AND posts.deleted = 0", (post_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    
    return dict(row)

def delete_post(post_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE posts SET deleted = 1 WHERE id = ?", (post_id,))
        connection.commit()
        return True, cursor.lastrowid
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def get_feed_posts(user_id, limit=10, offset=0):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT posts.*, users.username, (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count FROM posts JOIN users ON posts.user_id = users.id WHERE posts.deleted = 0 AND (posts.user_id = ? OR posts.user_id IN (SELECT followed_id FROM follows WHERE follower_id = ?)) ORDER BY posts.created DESC LIMIT ? OFFSET ?", (user_id, user_id, limit, offset))
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results


def get_global_feed_posts(limit=10, offset=0):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT posts.*, users.username, (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count FROM posts JOIN users ON posts.user_id = users.id WHERE posts.deleted = 0 ORDER BY posts.created DESC LIMIT ? OFFSET ?", (limit, offset))
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results


def get_posts_by_id(user_id, limit=10, offset=0):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT posts.*, users.username, (SELECT COUNT(*) FROM likes WHERE post_id = posts.id) AS like_count FROM posts JOIN users ON posts.user_id = users.id WHERE posts.user_id = ? AND posts.deleted = 0 ORDER BY posts.created DESC LIMIT ? OFFSET ?", (user_id, limit, offset))
                   
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def change_user_display_name(user_id, new_display_name):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE users SET display_name = ? WHERE id = ?", (new_display_name, user_id))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def like_post(user_id, post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    if cursor.fetchone() is not None:
        return False, "You have already liked this post."
    
    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO likes (user_id, post_id, created) VALUES (?, ?, ?)", (user_id, post_id, now_timestamp))
        connection.commit()
        return True, cursor.lastrowid

    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"

def unlike_post(user_id, post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    row = cursor.fetchone()
    if row is None:
        return False, "You have not liked this post."
    
    try:
        cursor.execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
        connection.commit()
        return True, row["id"]

    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"

def get_post_likes(post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT users.id, users.username FROM likes JOIN users ON likes.user_id = users.id WHERE likes.post_id = ? ORDER BY likes.created DESC", (post_id,))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results

def get_posts_count(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM posts WHERE user_id = ? AND deleted = 0", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return 0
    
    return row["count"]

def follow_user(current_user_id, target_user_id):
    if current_user_id == target_user_id:
        return False, "You cannot follow yourself."
    
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM follows WHERE follower_id = ? AND followed_id = ?", (current_user_id, target_user_id))
    if cursor.fetchone() is not None:
        return False, "You are already following this user."
    
    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO follows (follower_id, followed_id, created) VALUES (?, ?, ?)", (current_user_id, target_user_id, now_timestamp))
        connection.commit()
        return True, cursor.lastrowid
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def unfollow_user(current_user_id, target_user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM follows WHERE follower_id = ? AND followed_id = ?", (current_user_id, target_user_id))
    row = cursor.fetchone()
    if row is None:
        return False, "You are not following this user."
    
    try:
        cursor.execute("DELETE FROM follows WHERE follower_id = ? AND followed_id = ?", (current_user_id, target_user_id))
        connection.commit()
        return True, row["id"]
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def get_followers(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT users.id, users.username FROM follows JOIN users ON follows.follower_id = users.id WHERE follows.followed_id = ? ORDER BY follows.created DESC", (user_id,))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results

def get_following(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT users.id, users.username FROM follows JOIN users ON follows.followed_id = users.id WHERE follows.follower_id = ? ORDER BY follows.created DESC", (user_id,))
    
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results

def get_followers_count(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM follows WHERE followed_id = ?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return 0
    
    return row["count"]

def get_following_count(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM follows WHERE follower_id = ?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return 0
    
    return row["count"]

def is_following(follower_id, followed_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM follows WHERE follower_id = ? AND followed_id = ?", (follower_id, followed_id))
    row = cursor.fetchone()
    if row is None:
        return False
    
    return True

def create_comment(user_id, post_id, content):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO comments (user_id, post_id, content, created) VALUES (?, ?, ?, ?)", (user_id, post_id, content, now_timestamp))
        connection.commit()

        return True, cursor.lastrowid
    
    except Exception as e:
        return False, f"Error: {e}"
    
def get_comments_by_post(post_id, limit):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT comments.*, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.post_id = ? AND comments.deleted = 0 ORDER BY comments.created DESC LIMIT ?", (post_id, limit))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def get_comments_count(post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM comments WHERE post_id = ? AND deleted = 0", (post_id,))
    row = cursor.fetchone()
    if row is None:
        return 0
    
    count = row["count"]

    return count

def get_comment(comment_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT comments.*, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.id = ? AND comments.deleted = 0", (comment_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    
    return dict(row)

def delete_comment(comment_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE comments SET deleted = 1 WHERE id = ?", (comment_id,))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def send_message(sender_id, receiver_id, content):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, content, created) VALUES (?, ?, ?, ?)", (sender_id, receiver_id, content, now_timestamp))
        connection.commit()
        return True, cursor.lastrowid
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"

def get_messages(user_id, other_id, limit=20):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT messages.*, sender.username AS sender_username, receiver.username AS receiver_username FROM messages JOIN users AS sender ON messages.sender_id = sender.id JOIN users AS receiver ON messages.receiver_id = receiver.id WHERE (messages.sender_id = ? AND messages.receiver_id = ?) OR (messages.sender_id = ? AND messages.receiver_id = ?) ORDER BY messages.created ASC LIMIT ?", (user_id, other_id, other_id, user_id, limit))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def get_conversations(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END AS other_id, content AS last_message, MAX(created) AS timestamp FROM messages WHERE sender_id = ? OR receiver_id = ? GROUP BY other_id ORDER BY timestamp DESC", (user_id, user_id, user_id))

    results = []

    for row in cursor.fetchall():
        user = get_user_by_id(row["other_id"])

        if user:
            results.append({
                "id": user["id"],
                "username": user["username"],
                "last_message": row["last_message"],
                "timestamp": row["timestamp"]
            })

    return results

def update_user(user_id, **kwargs):
    connection = connect_db()
    cursor = connection.cursor()

    allowed_fields = ["display_name", "bio", "status", "location", "website", "profile_ascii", "is_banned", "ban_reason", "is_admin", "is_verified", "is_private"]

    updates = []
    values = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f"{field} = ?")
            values.append(value)
    
    if not updates:
        return False
    
    values.append(user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"

    cursor.execute(query, values)
    connection.commit()

    return True

def create_admin():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM users WHERE is_admin = 1")
    admin = cursor.fetchone()

    if admin is None:
        password_hash, password_salt = hash_password(DEFAULT_ADMIN_PASSWORD)
        now_timestamp = timestamp()

        cursor.execute("INSERT INTO users (username, password_hash, password_salt, created, is_admin, bio, is_verified) VALUES (?, ?, ?, ?, 1, ?, ?)", ("admin", password_hash, password_salt, now_timestamp, "Admin", 1))
        connection.commit()

def admin_log(admin_id, action, target_user_id=None, details=None):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO admin_logs (admin_id, action, target_user_id, details, created) VALUES (?, ?, ?, ?, ?)", (admin_id, action, target_user_id, details, now_timestamp))
        connection.commit()

    except Exception as e:
        print(f"Error logging admin action: {e}")

def get_admin_logs(limit, offset):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT admin_logs.*, users.username AS admin_username FROM admin_logs JOIN users ON admin_logs.admin_id = users.id ORDER BY admin_logs.created DESC LIMIT ? OFFSET ?", (limit, offset))
    
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results

def get_statistics():
    connection = connect_db()
    cursor = connection.cursor()

    stats = {}

    cursor.execute("SELECT COUNT(*) AS user_count FROM users")
    row = cursor.fetchone()
    if row:
        stats["user_count"] = row["user_count"]
    else:
        stats["user_count"] = 0

    cursor.execute("SELECT COUNT(*) AS banned_count FROM users WHERE is_banned = 1")
    row = cursor.fetchone()
    if row:
        stats["banned_count"] = row["banned_count"]
    else:
        stats["banned_count"] = 0

    cursor.execute("SELECT COUNT(*) AS post_count FROM posts WHERE deleted = 0")
    row = cursor.fetchone()
    if row:
        stats["post_count"] = row["post_count"]
    else:
        stats["post_count"] = 0

    cursor.execute("SELECT COUNT(*) AS like_count FROM likes")
    row = cursor.fetchone()
    if row:
        stats["like_count"] = row["like_count"]
    else:
        stats["like_count"] = 0

    cursor.execute("SELECT COUNT(*) AS follow_count FROM follows")
    row = cursor.fetchone()
    if row:
        stats["follow_count"] = row["follow_count"]
    else:
        stats["follow_count"] = 0

    return stats
