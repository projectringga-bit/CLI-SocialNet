import db
import auth
import ascii
from utils import print_post, print_separator


def create_post(content, image_path=None, image_url=None):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if len(content) > 500:
        return False, "Post content cannot exceed 500 characters."
    
    image_ascii = None
    if image_path is not None:
        success, result = ascii.image_to_ascii(image_path)

        if not success:
            return False, result
        
        image_ascii = result

    elif image_url is not None:
        success, result = ascii.image_url_to_ascii(image_url)

        if not success:
            return False, result
        
        image_ascii = result
    
    user = auth.get_current_user()

    success, result = db.create_post(user["id"], content, image_ascii)

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
    
    success, result = db.delete_post(post_id)

    if success:
        return True, f"Post #{post_id} deleted."
    else:
        return False, result


def get_home_feed():
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()

    offset = 0
    
    posts = db.get_feed_posts(user["id"], limit=10, offset=offset)

    return posts


def get_feed(page=1):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    
    offset = (page - 1) * 10

    posts = db.get_feed_posts(user["id"], limit=10, offset=offset)

    return posts


def get_global_feed(page=1):
    offset = (page - 1) * 10

    posts = db.get_global_feed_posts(limit=10, offset=offset)

    return posts


def get_my_posts(page=1):
    if not auth.is_logged():
        return []
    
    user = auth.get_current_user()

    offset = (page - 1) * 10
    
    posts = db.get_posts_by_id(user["id"], limit=10, offset=offset)

    return posts


def view_post(post_id):
    post = db.get_post(post_id)

    return post


def display_single_post(post_id):
    post = view_post(post_id)

    if post is None:
        return False, "Post not found."
    
    print_post(post)

    likes, _ = get_likes(post_id)
    if likes:
        usernames = []

        for like in likes[:5]:
            usernames.append(f"@{like['username']}")
        
        if len(likes) > 5:
            usernames.append(f"and {len(likes) - 5} more")
        
        print(f"    Liked by: {', '.join(usernames)}")
    
    print_separator()

    return True, None


def display_multiple_posts(posts, title):
    if not posts:
        return False, "No posts to display."
    
    print(f"\n{title}:")

    for post in posts:
        print_post(post)

    print_separator()

    return True, None


""" def view_user_posts(username):
    user = db.get_user_by_username(username)

    if user is None:
        return []
    
    posts = db.get_posts_by_id(user["id"])

    return posts """


def like_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    post = db.get_post(post_id)

    if post is None:
        return False, "Post not found."
    
    user = auth.get_current_user()

    success, result = db.like_post(user["id"], post_id)

    if success:
        return True, f"Post #{post_id} liked."
    else:
        return False, result
    

def unlike_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    post = db.get_post(post_id)
    if post is None:
        return False, "Post not found."
    
    user = auth.get_current_user()

    success, result = db.unlike_post(user["id"], post_id)

    if success:
        return True, f"Post #{post_id} unliked."
    else:
        return False, result
    

def get_likes(post_id):
    post = db.get_post(post_id)

    if post is None:
        return False, "Post not found."
    
    likes = db.get_post_likes(post_id)

    return likes, None
