import db
import auth
from utils import print_separator

def ban_user(username, reason="No reason provided"):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_user_by_username(username)
    if target is None:
        return False, "User not found."
    
    current_user = auth.get_current_user()
    if target["id"] == current_user["id"]:
        return False, "You cannot ban yourself."
    
    db.update_user(target["id"], is_banned=1, ban_reason=reason)

    db.delete_user_sessions(target["id"]) 

    return True, f"User @{username} has been banned."


def unban_user(username):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_user_by_username(username)
    if target is None:
        return False, "User not found."
    
    if target["is_banned"] == 0:
        return False, "User is not banned."
    
    db.update_user(target["id"], is_banned=0, ban_reason="")

    return True, f"User @{username} has been unbanned."


def delete_post(post_id):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_post(post_id)
    if target is None:
        return False, "Post not found."
    
    db.delete_post(post_id)

    return True, f"Post #{post_id} has been deleted."


def get_stats():
    if not auth.is_admin():
        return None
    
    stats = db.get_statistics()

    return stats


def print_banner_admin():
    if not auth.is_admin():
        return
    
    stats = get_stats()

    print("\n ADMIN DASHBOARD")

    print_separator()

    print("Statistics:")
    print(f"    Users: {stats.get("user_count")} (Banned: {stats.get("banned_count")})")
    print(f"    Posts: {stats.get("post_count")}")
    print(f"    Likes: {stats.get("like_count")}")
    print(f"    Follows: {stats.get("follow_count")}")

    print("\n Admin commands:")
    print("    admin                              -> View platform statistics")
    print("    admin ban <username> [reason]      -> Ban a user")
    print("    admin unban <username>             -> Unban a user")
    print("    admin deletepost <post_id>         -> Delete a post")

    print_separator()
    