import db
import auth


def create_post(content):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if not content:
        return False, "Post content cannot be empty."
    
    if len(content) > 500:
        return False, "Post content cannot exceed 500 characters."
    
    user = auth.get_current_user()

    success, result = db.create_post(user["id"], content)

    if success:
        return True, f"Post created! ID: {result}"
    else:
        return False, result


def delete_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    post = db.get_post(post_id)

    if post is None:
        return False, "Post not found."
    
    user = auth.get_current_user()

    if post["user_id"] != user["id"]:
        return False, "You can only delete your own posts."
    
    db.delete_post(post_id)

    return True, "Post deleted."


def get_home_feed():
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    
    posts = db.get_feed_posts(user["id"])

    return posts


def view_post(post_id):
    post = db.get_post(post_id)

    return post


def view_user_posts(username):
    user = db.get_user_by_username(username)

    if user is None:
        return []
    
    posts = db.get_posts_by_username(user["id"])

    return posts
