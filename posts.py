import db
import auth
import ascii
from utils import print_post, print_separator, print_comment


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
        post_id = result
        db.hashtag_detection(post_id, content)
        db.mention_detection(post_id, content, user["id"])

        return True, f"Post created! ID: {result}"
    
    else:
        return False, result
    

def create_post_big(big_text, content=""):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if len(content) > 500:
        return False, "Post content cannot exceed 500 characters."
    
    if len(big_text) > 7:
        return False, "Big text content cannot exceed 7 characters."
    
    success, result = ascii.text_to_ascii(big_text)

    if not success:
        return False, result
    
    image_ascii = result

    user = auth.get_current_user()

    success, result = db.create_post(user["id"], content, image_ascii)

    if success:
        post_id = result
        db.hashtag_detection(post_id, content)
        db.mention_detection(post_id, content, user["id"])

        return True, f"Post created! ID: {result}"
    
    else:
        return False, result
    

def create_poll_post(content, question, options):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    if len(content) > 500:
        return False, "Post content cannot exceed 500 characters."
    
    if len(question) > 500:
        return False, "Poll question cannot exceed 500 characters."
    
    if len(options) > 20:
        return False, "Poll must have no more than 20 options."
    
    option_a = []
    for option in options:
        if len(option) > 50:
            return False, "Each poll option cannot exceed 50 characters."
        
        option_a.append(option)
    
    user = auth.get_current_user()

    success, result = db.create_poll(user["id"], content, question, option_a)

    if success:
        post_id = result
        db.hashtag_detection(post_id, content)
        db.mention_detection(post_id, content, user["id"])

        return True, f"Poll post created! ID: {result}"
    
    else:
        return False, result


def delete_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."

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
    
    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]

    posts = db.get_global_feed_posts(limit=10, offset=offset, viewer_id=viewer_id)

    return posts


def get_my_posts(page=1):
    if not auth.is_logged():
        return []
    
    user = auth.get_current_user()

    offset = (page - 1) * 10
    
    posts = db.get_posts_by_id(user["id"], limit=10, offset=offset, viewer_id=user["id"])

    return posts


def view_post(post_id):
    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]
    
    post = db.get_post(post_id, viewer_id=viewer_id)

    return post


def display_single_post(post_id):
    post = view_post(post_id)

    if post is None:
        return False, "Post not found."
    
    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]
    
    print_post(post)

    likes, _ = get_likes(post_id)
    if likes:
        usernames = []

        for like in likes[:5]:
            usernames.append(f"@{like['username']}")
        
        if len(likes) > 5:
            usernames.append(f"and {len(likes) - 5} more")
        
        print(f"    Liked by: {', '.join(usernames)}")
        
    comment_count = db.get_comments_count(post_id)
    comments = db.get_comments_by_post(post_id, limit=3, viewer_id=viewer_id)
    if comment_count > 0:
        print(f"\n    Comments: {comment_count}")

        for comment in comments:
            print_comment(comment)
    
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


def repost(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])
    if post is None:
        return False, "Post not found."

    success, result = db.create_repost(user["id"], post_id)
    
    if success:
        return True, f"Post #{post_id} reposted."
    else:
        return False, result
    

def quote_post(post_id, content):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."
    
    if len(content) > 500:
        return False, "Quote content cannot exceed 500 characters."
    
    user = auth.get_current_user()

    success, result = db.create_repost(user["id"], post_id, content)

    if success:
        return True, f"Post #{post_id} quoted."
    else:
        return False, result
    

def unrepost(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."
    
    user = auth.get_current_user()

    success, result = db.delete_repost(user["id"], post_id)

    if success:
        return True, f"Repost of post #{post_id} removed."
    else:
        return False, result
    

def get_reposts(post_id):
    viewer_id = None
    if auth.is_logged():
        user = auth.get_current_user()
        viewer_id = user["id"]
    
    post = db.get_post(post_id, viewer_id=viewer_id)

    if post is None:
        return False, "Post not found."
    
    reposts = db.get_reposts(post_id, viewer_id=viewer_id)

    return True, reposts


def bookmark_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."

    success, result = db.create_bookmark(user["id"], post_id)

    if success:
        return True, f"Post #{post_id} bookmarked."
    else:
        return False, result


def unbookmark_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."
    
    success, result = db.remove_bookmark(user["id"], post_id)

    if success:
        return True, f"Post #{post_id} unbookmarked."
    else:
        return False, result
    

def get_bookmarks(page):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()

    bookmarks = db.get_bookmarks(user["id"], page=page)

    return True, bookmarks


def pin_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."

    if post["user_id"] != user["id"]:
        return False, "You can only pin your own posts."

    success, result = db.pin_post(user["id"], post_id)

    if success:
        return True, f"Post #{post_id} pinned."
    else:
        return False, result
    

def unpin_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."
    
    if post["user_id"] != user["id"]:
        return False, "You can only unpin your own posts."
    
    success, result = db.unpin_post(user["id"], post_id)

    if success:
        return True, f"Post #{post_id} unpinned."
    else:
        return False, result
    

def get_pinned_posts_by_user(username):
    user = db.get_user_by_username(username)
    if user is None:
        return False, "User not found."
    
    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]

    pinned_posts = db.get_pinned_posts(user["id"], viewer_id=viewer_id)

    return True, pinned_posts


def search_hashtag(hashtag, page=1):
    offset = (page - 1) * 10

    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]

    posts = db.get_posts_using_hashtag(hashtag, limit=10, offset=offset, viewer_id=viewer_id)

    return True, posts


def trending_hashtags():
    hashtags = db.get_trending_hashtags(10)

    return True, hashtags


def search_hashtags(hashtag, page=1):
    offset = (page - 1) * 10

    hashtags = db.search_hashtags(hashtag, limit=20, offset=offset)

    return True, hashtags


def get_mentions(username, page=1):
    offset = (page - 1) * 10

    user = db.get_user_by_username(username)
    if user is None:
        return False, "User not found."
    
    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]

    posts = db.get_posts_mentioning_username(user["id"], limit=10, offset=offset, viewer_id=viewer_id)

    return True, posts


def like_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."

    success, result = db.like_post(user["id"], post_id)

    if success:
        return True, f"Post #{post_id} liked."
    else:
        return False, result
    

def unlike_post(post_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."
    
    success, result = db.unlike_post(user["id"], post_id)

    if success:
        return True, f"Post #{post_id} unliked."
    else:
        return False, result
    

def get_likes(post_id):
    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]
    
    post = db.get_post(post_id, viewer_id=viewer_id)

    if post is None:
        return False, "Post not found."
    
    likes = db.get_post_likes(post_id)

    return likes, None


def comment(post_id, content):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    post = db.get_post(post_id, viewer_id=user["id"])

    if post is None:
        return False, "Post not found."
    
    if len(content) > 500:
        return False, "Comment content cannot exceed 500 characters."
    
    success, result = db.create_comment(user["id"], post_id, content)

    if success:
        return True, f"Comment added to post #{post_id}."
    else:
        return False, result
    

def delete_comment(comment_id):
    if not auth.is_logged():
        return False, "You must be logged in."
    
    comment = db.get_comment(comment_id)
    if comment is None:
        return False, "Comment not found."
    
    user = auth.get_current_user()
    post = db.get_post(comment["post_id"], viewer_id=user["id"])

    if comment["user_id"] != user["id"]:
        return False, "You can only delete your own comments under other users posts."

    if post and post["user_id"] != user["id"]:
        return False, "You can only delete comments on your own posts."
    
    db.delete_comment(comment_id)

    return True, f"Comment #{comment_id} deleted."


def get_post_comments(post_id, limit=50):
    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]

    post = db.get_post(post_id, viewer_id=viewer_id)
    if post is None:
        return False, "Post not found."
    
    comments = db.get_comments_by_post(post_id, limit=limit, viewer_id=viewer_id)

    return True, comments


def search_posts(query, page=1):
    offset = (page - 1) * 10

    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]

    posts = db.search_posts(query, limit=10, offset=offset, viewer_id=viewer_id)

    return True, posts

def get_poll_by_post_id(post_id):
    viewer_id = None
    if auth.is_logged():
        current_user = auth.get_current_user()
        viewer_id = current_user["id"]
    
    poll = db.get_poll_by_post_id(post_id, viewer_id=viewer_id)
    
    return poll

def vote_poll(user_id, poll_id, option_id, post_id):    
    success, result = db.vote_poll(user_id, poll_id, option_id)

    if success:
        return True, f"Vote recorded on post #{post_id}."
    else:
        return False, result
