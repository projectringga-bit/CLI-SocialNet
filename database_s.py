import sqlite3
import re

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
                    "is_verified INTEGER DEFAULT 0," \
                    "login_attempts INTEGER DEFAULT 0," \
                    "locked_until INTEGER DEFAULT 0)" )
    
    # Limit registrations
    cursor.execute("CREATE TABLE IF NOT EXISTS registration_limits ("
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "machine_id TEXT NOT NULL," \
                   "username TEXT, " \
                   "created INTEGER NOT NULL)" )
    
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
    
    # reposts table
    cursor.execute("CREATE TABLE IF NOT EXISTS reposts (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "user_id INTEGER NOT NULL," \
                   "post_id INTEGER NOT NULL," \
                   "content TEXT DEFAULT NULL," \
                   "created INTEGER NOT NULL," \
                   "is_deleted INTEGER DEFAULT 0," \
                   "FOREIGN KEY (user_id) REFERENCES users(id)," \
                   "FOREIGN KEY (post_id) REFERENCES posts(id))")
    
    # bookmarks table
    cursor.execute("CREATE TABLE IF NOT EXISTS bookmarks (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "user_id INTEGER NOT NULL," \
                   "post_id INTEGER NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (user_id) REFERENCES users(id)," \
                   "FOREIGN KEY (post_id) REFERENCES posts(id)," \
                   "UNIQUE(user_id, post_id))")  

    # pinned posts table
    cursor.execute("CREATE TABLE IF NOT EXISTS pinned_posts (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "user_id INTEGER NOT NULL," \
                   "post_id INTEGER NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (user_id) REFERENCES users(id)," \
                   "FOREIGN KEY (post_id) REFERENCES posts(id)," \
                   "UNIQUE(user_id, post_id))")
    
    # hashtags table
    cursor.execute("CREATE TABLE IF NOT EXISTS hashtags (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "hashtag TEXT UNIQUE NOT NULL," \
                   "created INTEGER NOT NULL)")
    
    # "post linked to hashtags" table
    cursor.execute("CREATE TABLE IF NOT EXISTS post_hashtags (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "post_id INTEGER NOT NULL," \
                   "hashtag_id INTEGER NOT NULL," \
                   "FOREIGN KEY (post_id) REFERENCES posts(id)," \
                   "FOREIGN KEY (hashtag_id) REFERENCES hashtags(id)," \
                   "UNIQUE(post_id, hashtag_id))")
    
    # mentions table
    cursor.execute("CREATE TABLE IF NOT EXISTS mentions (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "post_id INTEGER NOT NULL," \
                   "mentioned_user INTEGER NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (post_id) REFERENCES posts(id)," \
                   "FOREIGN KEY (mentioned_user) REFERENCES users(id)," \
                   "UNIQUE(post_id, mentioned_user))")
    
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
                   "is_read INTEGER DEFAULT 0," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (sender_id) REFERENCES users(id)," \
                   "FOREIGN KEY (receiver_id) REFERENCES users(id))")
    
    # Closed conversations table
    cursor.execute("CREATE TABLE IF NOT EXISTS closed_conversations (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "user_id INTEGER NOT NULL," \
                   "other_user_id INTEGER NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (user_id) REFERENCES users(id)," \
                   "FOREIGN KEY (other_user_id) REFERENCES users(id)," \
                   "UNIQUE(user_id, other_user_id))")
    
    # Notifications table
    cursor.execute("CREATE TABLE IF NOT EXISTS notifications (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "user_id INTEGER NOT NULL," \
                   "type TEXT NOT NULL," \
                   "content TEXT NOT NULL," \
                   "is_read INTEGER DEFAULT 0," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (user_id) REFERENCES users(id))")
                   
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
    
    # Aliases table
    cursor.execute("CREATE TABLE IF NOT EXISTS command_aliases (" \
                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                   "user_id INTEGER NOT NULL," \
                   "alias TEXT NOT NULL," \
                   "command TEXT NOT NULL," \
                   "created INTEGER NOT NULL," \
                   "FOREIGN KEY (user_id) REFERENCES users(id)," \
                   "UNIQUE(user_id, alias))")


    connection.commit()

    create_admin()

    return True


def can_view_content(viewer_id, content_owner_id):
    connection = connect_db()
    cursor = connection.cursor()
    
    if viewer_id == content_owner_id:
        return True
    
    cursor.execute("SELECT is_private FROM users WHERE id = ?", (content_owner_id,))
    row1 = cursor.fetchone()

    if row1 is None:
        return False
    
    if row1["is_private"] == 0:
        return True
    
    cursor.execute("SELECT id FROM follows WHERE follower_id = ? AND followed_id = ?", (viewer_id, content_owner_id))
    viewer_follows_the_owner = cursor.fetchone()

    cursor.execute("SELECT id FROM follows WHERE follower_id = ? AND followed_id = ?", (content_owner_id, viewer_id))
    owner_follows_the_viewer = cursor.fetchone()

    if viewer_follows_the_owner and owner_follows_the_viewer:
        return True
    
    return False


def create_user(username, password, machine_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    if machine_id is not None:
        hour = now_timestamp - 3600

        cursor.execute("SELECT COUNT(*) AS count FROM registration_limits WHERE machine_id = ? AND created > ?", (machine_id, hour))
        row = cursor.fetchone()
        if row["count"] >= 3:
            return False, "Registration limit exceeded for this machine. Please try again later."

    cursor.execute("SELECT id FROM users WHERE username = ?", (username.lower(),))
    if cursor.fetchone() is not None:
        return False, "Username is already taken."
    
    password_hash, password_salt = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash, password_salt, created) VALUES (?, ?, ?, ?)", (username.lower(), password_hash, password_salt, now_timestamp))
        connection.commit()

        if machine_id is not None:
            cursor.execute("INSERT INTO registration_limits (machine_id, username, created) VALUES (?, ?, ?)", (machine_id, username.lower(), now_timestamp))
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
    
def get_post(post_id, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT posts.*, users.username, (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count, (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count, (SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count FROM posts JOIN users ON posts.user_id = users.id WHERE posts.id = ? AND posts.deleted = 0", (post_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    
    post = dict(row)

    if viewer_id is not None:
        if not can_view_content(viewer_id, post["user_id"]):
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

    cursor.execute("SELECT posts.*, users.username," \
                   "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                   "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                   "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                   "FROM posts JOIN users ON posts.user_id = users.id WHERE posts.deleted = 0 AND (posts.user_id = ? OR (posts.user_id IN (SELECT followed_id FROM follows WHERE follower_id = ?) AND (users.is_private = 0 OR EXISTS (SELECT 1 FROM follows WHERE follower_id = posts.user_id AND followed_id = ?)))) ORDER BY posts.created DESC LIMIT ? OFFSET ?", (user_id, user_id, user_id, limit, offset))
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results


def get_global_feed_posts(limit=10, offset=0, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    if viewer_id is None:
        cursor.execute("SELECT posts.*, users.username," \
                       "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                       "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                       "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                       "FROM posts JOIN users ON posts.user_id = users.id WHERE posts.deleted = 0 AND users.is_private = 0 ORDER BY posts.created DESC LIMIT ? OFFSET ?", (limit, offset))
    else:
        cursor.execute("SELECT posts.*, users.username," \
                       "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                       "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                       "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                       "FROM posts JOIN users ON posts.user_id = users.id WHERE posts.deleted = 0 AND (users.is_private = 0 OR (EXISTS (SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = users.id) AND EXISTS (SELECT 1 FROM follows WHERE follower_id = users.id AND followed_id = ?))) ORDER BY posts.created DESC LIMIT ? OFFSET ?", (viewer_id, viewer_id, limit, offset))
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results


def get_posts_by_id(user_id, limit=10, offset=0, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    if viewer_id is not None:
        if not can_view_content(viewer_id, user_id):
            return []

    cursor.execute("""
    SELECT posts.*, users.username,
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count,
        (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count,
        (SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count,
        NULL AS repost_id, NULL AS repost_username, NULL AS quote_content, posts.created AS original_created
    FROM posts JOIN users ON posts.user_id = users.id WHERE posts.user_id = ? AND posts.deleted = 0
    """, (user_id,))
                   
    results = []

    for row in cursor.fetchall():
        results.append(dict(row))

    cursor.execute("""
    SELECT posts.*, users.username,
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count,
        (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count,
        (SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count,
        reposts.id AS repost_id, reposting_user.username AS repost_username, reposts.content AS quote_content, reposts.created AS original_created
    FROM reposts JOIN posts ON reposts.post_id = posts.id JOIN users ON posts.user_id = users.id JOIN users AS reposting_user ON reposts.user_id = reposting_user.id
    WHERE reposts.user_id = ? AND reposts.is_deleted = 0 AND posts.deleted = 0
    """, (user_id,))

    for row in cursor.fetchall():
        results.append(dict(row))

    results.sort(key=lambda x: x.get("original_created"), reverse=True)
    
    return results[offset: offset + limit]

def get_post_owner(post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    
    return row["user_id"]
    
def like_post(user_id, post_id):
    connection = connect_db()
    cursor = connection.cursor()

    owner = get_post_owner(post_id)
    if not can_view_content(user_id, owner):
        return False, "You cannot like this post."

    cursor.execute("SELECT id FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    if cursor.fetchone() is not None:
        return False, "You have already liked this post."
    
    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO likes (user_id, post_id, created) VALUES (?, ?, ?)", (user_id, post_id, now_timestamp))
        connection.commit()

        owner = get_post_owner(post_id)
        if owner != user_id:
            user = get_user_by_id(user_id)
            create_notification(owner, "like", f"User @{user['username']} liked your #{post_id} post.")

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

def create_bookmark(user_id, post_id):
    connection = connect_db()
    cursor = connection.cursor()

    owner = get_post_owner(post_id)
    if not can_view_content(user_id, owner):
        return False, "You cannot bookmark this post."

    cursor.execute("SELECT id FROM bookmarks WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    if cursor.fetchone() is not None:
        return False, "Post is already bookmarked."
    
    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO bookmarks (user_id, post_id, created) VALUES (?, ?, ?)", (user_id, post_id, now_timestamp))
        connection.commit()

        return True, cursor.lastrowid

    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def remove_bookmark(user_id, post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM bookmarks WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    row = cursor.fetchone()
    if row is None:
        return False, "Post is not bookmarked."
    
    try:
        cursor.execute("DELETE FROM bookmarks WHERE user_id = ? AND post_id = ?", (user_id, post_id))
        connection.commit()
        return True, row["id"]
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def get_bookmarks(user_id, limit = 5, page=1):
    connection = connect_db()
    cursor = connection.cursor()

    offset = (page - 1) * limit

    cursor.execute("SELECT posts.*, users.username, bookmarks.created as bookmark_created, (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count, (SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id AND reposts.is_deleted = 0) AS repost_count, (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id AND comments.deleted = 0) AS comment_count FROM bookmarks JOIN posts ON bookmarks.post_id = posts.id JOIN users ON posts.user_id = users.id WHERE bookmarks.user_id = ? AND posts.deleted = 0 ORDER BY bookmarks.created DESC LIMIT ? OFFSET ?", (user_id, limit, offset))
    
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results

def pin_post(user_id, post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM pinned_posts WHERE user_id = ?", (user_id,))
    if cursor.fetchone()["count"] >= 3:
        return False, "You can only pin up to 3 posts."

    cursor.execute("SELECT id FROM pinned_posts WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    if cursor.fetchone() is not None:
        return False, "Post is already pinned."
    
    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO pinned_posts (user_id, post_id, created) VALUES (?, ?, ?)", (user_id, post_id, now_timestamp))
        connection.commit()
        return True, cursor.lastrowid
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def unpin_post(user_id, post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM pinned_posts WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    row = cursor.fetchone()
    if row is None:
        return False, "Post is not pinned."
    
    try:
        cursor.execute("DELETE FROM pinned_posts WHERE user_id = ? AND post_id = ?", (user_id, post_id))
        connection.commit()
        return True, row["id"]
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def get_pinned_posts(user_id, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    if viewer_id is not None:
        if not can_view_content(viewer_id, user_id):
            return []

    cursor.execute("SELECT posts.*, users.username, (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count, (SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id AND reposts.is_deleted = 0) AS repost_count FROM pinned_posts JOIN posts ON pinned_posts.post_id = posts.id JOIN users ON posts.user_id = users.id WHERE pinned_posts.user_id = ? AND posts.deleted = 0 ORDER BY pinned_posts.created DESC", (user_id,))
    
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def hashtag_detection(post_id, content):
    connection = connect_db()
    cursor = connection.cursor()

    hashtags = re.findall(r"#(\w+)", content)

    for hashtag in hashtags:
        hashtag_lower = hashtag.lower().strip()

        cursor.execute("SELECT id FROM hashtags WHERE hashtag = ?", (hashtag_lower,))
        row = cursor.fetchone()
        if row is None:
            now_timestamp = timestamp()

            cursor.execute("INSERT INTO hashtags (hashtag, created) VALUES (?, ?)", (hashtag_lower, now_timestamp))
            connection.commit()

            hashtag_id = cursor.lastrowid

        else:
            hashtag_id = row["id"]
        
        try:
            cursor.execute("INSERT OR IGNORE INTO post_hashtags (post_id, hashtag_id) VALUES (?, ?)", (post_id, hashtag_id))
            connection.commit()

        except Exception as e:
            print(f"Error: {e}")
            continue

        return hashtags


def get_posts_using_hashtag(hashtag, limit=10, offset=0, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    hashtag_lower = hashtag.lower().strip().lstrip("#")
    
    if viewer_id is None:
        cursor.execute("SELECT posts.*, users.username," \
                       "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                       "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                       "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                       "FROM posts JOIN users ON posts.user_id = users.id JOIN post_hashtags ON posts.id = post_hashtags.post_id JOIN hashtags ON post_hashtags.hashtag_id = hashtags.id WHERE hashtags.hashtag = ? AND posts.deleted = 0 AND users.is_banned = 0 AND users.is_private = 0 ORDER BY posts.created DESC LIMIT ? OFFSET ?", (hashtag_lower, limit, offset))

    else:
        cursor.execute("SELECT posts.*, users.username," \
                       "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                       "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                       "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                       "FROM posts JOIN users ON posts.user_id = users.id JOIN post_hashtags ON posts.id = post_hashtags.post_id JOIN hashtags ON post_hashtags.hashtag_id = hashtags.id WHERE hashtags.hashtag = ? AND posts.deleted = 0 AND users.is_banned = 0 AND (users.is_private = 0 OR (EXISTS (SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = users.id) AND EXISTS (SELECT 1 FROM follows WHERE follower_id = users.id AND followed_id = ?))) ORDER BY posts.created DESC LIMIT ? OFFSET ?", (hashtag_lower, viewer_id, viewer_id, limit, offset))
    
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def get_trending_hashtags(limit=10):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT hashtags.hashtag, COUNT(post_hashtags.post_id) AS usage_count FROM hashtags JOIN post_hashtags ON hashtags.id = post_hashtags.hashtag_id JOIN posts ON post_hashtags.post_id = posts.id WHERE posts.deleted = 0 GROUP BY hashtags.id ORDER BY usage_count DESC LIMIT ?", (limit,))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def search_hashtags(hashtag, limit, offset):
    connection = connect_db()
    cursor = connection.cursor()

    hashtag_search = f"{hashtag.lower().strip()}%"

    cursor.execute("SELECT hashtags.*, COUNT(post_hashtags.post_id) AS usage_count FROM hashtags LEFT JOIN post_hashtags ON hashtags.id = post_hashtags.hashtag_id WHERE hashtags.hashtag LIKE ? GROUP BY hashtags.id ORDER BY usage_count DESC LIMIT ? OFFSET ?", (hashtag_search, limit, offset))
    
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results

def mention_detection(post_id, content, user_id):
    connection = connect_db()
    cursor = connection.cursor()

    mentions = re.findall(r"@(\w+)", content)

    mentioned = []

    for username in mentions:
        user = get_user_by_username(username)
        if user and user["id"] != user_id:
            now_timestamp = timestamp()

            cursor.execute("INSERT OR IGNORE INTO mentions (post_id, mentioned_user, created) VALUES (?, ?, ?)", (post_id, user["id"], now_timestamp))
            connection.commit()
            
            mentioned.append(user)

            create_notification(user["id"], "mention", f"User @{get_user_by_id(user_id)['username']} mentioned you in their #{post_id} post.")

    return mentioned

def get_posts_mentioning_username(user_id, limit=10, offset=0, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    if viewer_id is None:
        cursor.execute("SELECT posts.*, users.username," \
                       "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                       "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                       "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                       "FROM mentions JOIN posts ON mentions.post_id = posts.id JOIN users ON posts.user_id = users.id WHERE mentions.mentioned_user = ? AND posts.deleted = 0 AND users.is_private = 0 ORDER BY posts.created DESC LIMIT ? OFFSET ?", (user_id, limit, offset))
    else:
        cursor.execute("SELECT posts.*, users.username," \
                       "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                       "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                       "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                       "FROM mentions JOIN posts ON mentions.post_id = posts.id JOIN users ON posts.user_id = users.id WHERE mentions.mentioned_user = ? AND posts.deleted = 0 AND (users.is_private = 0 OR (EXISTS (SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = users.id) AND EXISTS (SELECT 1 FROM follows WHERE follower_id = users.id AND followed_id = ?))) ORDER BY posts.created DESC LIMIT ? OFFSET ?", (user_id, viewer_id, viewer_id, limit, offset))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

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

        follower = get_user_by_id(current_user_id)
        create_notification(target_user_id, "follow", f"User @{follower['username']} started following you.")

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

def get_following(user_id, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    if viewer_id is not None:
        if not can_view_content(viewer_id, user_id):
            return []

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

def get_following_count(user_id, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    if viewer_id is not None:
        if not can_view_content(viewer_id, user_id):
            return 0

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
    
    owner = get_post_owner(post_id)
    if not can_view_content(user_id, owner):
        return False, "You cannot comment on this post."

    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO comments (user_id, post_id, content, created) VALUES (?, ?, ?, ?)", (user_id, post_id, content, now_timestamp))
        connection.commit()

        owner = get_post_owner(post_id)
        if owner != user_id:
            user = get_user_by_id(user_id)
            create_notification(owner, "comment", f"User @{user['username']} commented on your #{post_id} post.")

        return True, cursor.lastrowid
    
    except Exception as e:
        return False, f"Error: {e}"
    
def get_comments_by_post(post_id, limit, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    if viewer_id is not None:
        owner = get_post_owner(post_id)
        if not can_view_content(viewer_id, owner):
            return []

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
    
def create_repost(user_id, post_id, content=None):
    connection = connect_db()
    cursor = connection.cursor()

    owner = get_post_owner(post_id)
    if not can_view_content(user_id, owner):
        return False, "You cannot repost this post."

    cursor.execute("SELECT id FROM reposts WHERE user_id = ? AND post_id = ? AND is_deleted = 0", (user_id, post_id))
        
    if cursor.fetchone() is not None:
        return False, "You have already reposted this post."

    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO reposts (user_id, post_id, content, created) VALUES (?, ?, ?, ?)", (user_id, post_id, content, now_timestamp))
        connection.commit()
        
        owner = get_post_owner(post_id)
        if owner != user_id:
            user = get_user_by_id(user_id)
            if content:
                create_notification(owner, "quote_repost", f"User @{user['username']} quote reposted your #{post_id} post.")
            else:
                create_notification(owner, "repost", f"User @{user['username']} reposted your #{post_id} post.")

        return True, cursor.lastrowid
    
    except Exception as e:
        return False, f"Error: {e}"
    
def delete_repost(user_id, repost_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM reposts WHERE user_id = ? AND post_id = ? AND is_deleted = 0", (user_id, repost_id))
    row = cursor.fetchone()
    if row is None:
        return False, "You have not reposted this post."

    try:
        cursor.execute("UPDATE reposts SET is_deleted = 1 WHERE post_id = ? AND user_id = ?", (repost_id, user_id))
        connection.commit()
        return True, cursor.lastrowid
    
    except Exception as e:
        return False, f"Error: {e}"
    
def get_reposts_count(post_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM reposts WHERE post_id = ? AND is_deleted = 0", (post_id,))
    row = cursor.fetchone()
    if row is None:
        return 0
    
    return row["count"]

def get_reposts(post_id, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    if viewer_id is not None:
        owner = get_post_owner(post_id)
        if not can_view_content(viewer_id, owner):
            return []

    cursor.execute("SELECT reposts.*, users.username FROM reposts JOIN users ON reposts.user_id = users.id WHERE reposts.post_id = ? AND reposts.is_deleted = 0 ORDER BY reposts.created DESC", (post_id,))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def search_posts(query, limit=10, offset=0, viewer_id=None):
    connection = connect_db()
    cursor = connection.cursor()

    search_query = f"%{query.lower()}%"

    if viewer_id is None:
        cursor.execute("SELECT posts.*, users.username," \
                       "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                       "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                       "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                       "FROM posts JOIN users ON posts.user_id = users.id WHERE LOWER(posts.content) LIKE ? AND posts.deleted = 0 AND users.is_private = 0 ORDER BY posts.created DESC LIMIT ? OFFSET ?", (search_query, limit, offset))
    else:
        cursor.execute("SELECT posts.*, users.username," \
                       "(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count," \
                       "(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count," \
                       "(SELECT COUNT(*) FROM reposts WHERE reposts.post_id = posts.id and reposts.is_deleted = 0) AS repost_count " \
                       "FROM posts JOIN users ON posts.user_id = users.id WHERE LOWER(posts.content) LIKE ? AND posts.deleted = 0 AND (users.is_private = 0 OR (EXISTS (SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = users.id) AND EXISTS (SELECT 1 FROM follows WHERE follower_id = users.id AND followed_id = ?))) ORDER BY posts.created DESC LIMIT ? OFFSET ?", (search_query, viewer_id, viewer_id, limit, offset))
        
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def search_users(query, limit=10, offset=0):
    connection = connect_db()
    cursor = connection.cursor()

    search_query = f"%{query.lower()}%"

    cursor.execute("SELECT * FROM users WHERE LOWER(username) LIKE ? AND is_banned = 0 ORDER BY username ASC LIMIT ? OFFSET ?", (search_query, limit, offset))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))

    return results

def send_message(sender_id, receiver_id, content):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    try:
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, content, created) VALUES (?, ?, ?, ?)", (sender_id, receiver_id, content, now_timestamp))
        connection.commit()

        reopen_conversation(receiver_id, sender_id)
        reopen_conversation(sender_id, receiver_id)

        sender = get_user_by_id(sender_id)
        create_notification(receiver_id, "message", f"New message from @{sender['username']}")
        
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

    cursor.execute("SELECT CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END AS other_id, content AS last_message, MAX(created) AS timestamp FROM messages WHERE (sender_id = ? OR receiver_id = ?) AND other_id NOT IN (SELECT other_user_id FROM closed_conversations WHERE user_id = ?) GROUP BY other_id ORDER BY timestamp DESC", (user_id, user_id, user_id, user_id))

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

def close_conversation(user_id, other_id):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    try:
        cursor.execute("SELECT id FROM closed_conversations WHERE user_id = ? AND other_user_id = ?", (user_id, other_id))
        if cursor.fetchone() is not None:
            return False, "Conversation is already closed."
        
        cursor.execute("INSERT INTO closed_conversations (user_id, other_user_id, created) VALUES (?, ?, ?)", (user_id, other_id, now_timestamp))
        connection.commit()

        return True, cursor.lastrowid
    
    except Exception as e:
        print(f"Error: {e}")
        return False, f"Error: {e}"
    
def reopen_conversation(user_id, other_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM closed_conversations WHERE user_id = ? AND other_user_id = ?", (user_id, other_id))
        connection.commit()

        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_notification(user_id, type, content):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    cursor.execute("INSERT INTO notifications (user_id, type, content, created) VALUES (?, ?, ?, ?)", (user_id, type, content, now_timestamp))
    connection.commit()

def get_notifications(user_id, limit=20):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created DESC LIMIT ?", (user_id, limit))

    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    return results

def get_unread_notifications_count(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return 0
    
    return row["count"]

def get_unread_messages_count(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM messages WHERE receiver_id = ? AND is_read = 0", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return 0
    
    return row["count"]

def mark_notifications(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def mark_messages(user_id, sender):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE messages SET is_read = 1 WHERE receiver_id = ? AND sender_id = ?", (user_id, sender))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def clear_notifications(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def create_alias(user_id, alias, command):
    connection = connect_db()
    cursor = connection.cursor()

    now_timestamp = timestamp()

    try:
        cursor.execute("SELECT id FROM command_aliases WHERE user_id = ? AND alias = ?", (user_id, alias))

        if cursor.fetchone() is not None:
            cursor.execute("UPDATE command_aliases SET command = ?, created = ? WHERE user_id = ? AND alias = ?", (command, now_timestamp, user_id, alias))
            connection.commit()

            return True, f"Alias '{alias}' updated."
        
        else:
            cursor.execute("INSERT INTO command_aliases (user_id, alias, command, created) VALUES (?, ?, ?, ?)", (user_id, alias, command, now_timestamp))
            connection.commit()

            return True, f"Alias '{alias}' created."
        
    except Exception as e:
        return False, f"Error: {e}"
    
def get_user_aliases(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM command_aliases WHERE user_id = ? ORDER BY created DESC", (user_id,))

    results = {}
    for row in cursor.fetchall():
        results[row["alias"]] = row["command"]
    
    return results

def remove_alias(user_id, alias):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM command_aliases WHERE user_id = ? AND alias = ?", (user_id, alias))
        connection.commit()
        return True, f"Alias '{alias}' removed"
    
    except Exception as e:
        return False , f"Error: {e}"

def update_user(user_id, **kwargs):
    connection = connect_db()
    cursor = connection.cursor()

    allowed_fields = ["display_name", "bio", "status", "location", "website", "profile_ascii", "is_banned", "ban_reason", "is_admin", "is_verified", "is_private", "login_attempts", "locked_until"]

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
