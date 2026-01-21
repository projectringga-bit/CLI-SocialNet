import db
import auth
from utils import print_separator, format_timestamp, print_warning, pad_line

def ban_user(username, reason="No reason provided"):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_user_by_username(username)
    if target is None:
        return False, "User not found."
    
    if target["is_admin"] == 1:
        return False, "Cannot ban an admin user."
    
    current_user = auth.get_current_user()
    if target["id"] == current_user["id"]:
        return False, "You cannot ban yourself."
    
    db.update_user(target["id"], is_banned=1, ban_reason=reason)

    db.delete_user_sessions(target["id"]) 

    db.admin_log(current_user["id"], "ban_user", target["id"], f"Banned @{username} for reason: {reason}")

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

    current_user = auth.get_current_user()
    db.admin_log(current_user["id"], "unban_user", target["id"], f"Unbanned @{username}")

    return True, f"User @{username} has been unbanned."


def make_admin(username):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_user_by_username(username)
    if target is None:
        return False, "User not found."
    
    if target["is_admin"] == 1:
        return False, "User is already an admin."
    
    if target["is_banned"] == 1:
        return False, "Cannot make a banned user an admin."

    db.update_user(target["id"], is_admin=1)

    current_user = auth.get_current_user()
    db.admin_log(current_user["id"], "make_admin", target["id"], f"@{username} is now an admin")

    return True, f"User @{username} is now an admin."


def remove_admin(username):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_user_by_username(username)
    if target is None:
        return False, "User not found."
    
    if target["is_admin"] == 0:
        return False, "User is not an admin."
    
    if target["username"] == "admin":
        return False, "Cannot remove admin privileges from the main admin account."
    
    current_user = auth.get_current_user()
    if target["id"] == current_user["id"]:
        return False, "You cannot remove your own admin privileges."
    
    db.update_user(target["id"], is_admin=0)

    db.admin_log(current_user["id"], "remove_admin", target["id"], f"@{username} is no longer an admin")

    return True, f"User @{username} is no longer an admin."


def delete_post(post_id):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_post(post_id)
    if target is None:
        return False, "Post not found."
    
    db.delete_post(post_id)

    current_user = auth.get_current_user()
    db.admin_log(current_user["id"], "delete_post", target["id"], f"Deleted post #{post_id}")

    return True, f"Post #{post_id} has been deleted."


def verify_user(username):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_user_by_username(username)
    if target is None:
        return False, "User not found."
    
    if target["is_verified"] == 1:
        return False, "User is already verified."

    db.update_user(target["id"], is_verified=1)

    current_user = auth.get_current_user()
    db.admin_log(current_user["id"], "verify_user", target["id"], f"Verified @{username}")

    return True, f"User @{username} has been verified."


def unverify_user(username):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    target = db.get_user_by_username(username)
    if target is None:
        return False, "User not found."
    
    if target["is_verified"] == 0:
        return False, "User is not verified."

    db.update_user(target["id"], is_verified=0)

    current_user = auth.get_current_user()
    db.admin_log(current_user["id"], "unverify_user", target["id"], f"Unverified @{username}")

    return True, f"User @{username} has been unverified."


def get_stats():
    if not auth.is_admin():
        return None
    
    stats = db.get_statistics()

    return stats


def get_admin_logs(page=1):
    if not auth.is_admin():
        return False, "Admin privileges required."
    
    offset = (page - 1) * 50

    logs = db.get_admin_logs(limit=50, offset=offset)

    return True, logs


def print_banner_admin():
    if not auth.is_admin():
        return
    
    stats = get_stats()

    WIDTH = 80

    print()
    print("╔" + "═" * WIDTH + "╗")
    title_pad = (WIDTH - len(" ADMIN DASHBOARD ")) // 2
    print("║" + " " * title_pad + " ADMIN DASHBOARD " + " " * (WIDTH - len(" ADMIN DASHBOARD ") - title_pad) + "║")

    print("╠" + "═" * WIDTH + "╣")

    print("║" + pad_line("  STATISTICS", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")
    print("║" + pad_line(f"    Total Users:     {stats["user_count"]}", WIDTH) + "║")
    print("║" + pad_line(f"    Banned Users:    {stats["banned_count"]}", WIDTH) + "║")
    print("║" + pad_line(f"    Total Posts:     {stats["post_count"]}", WIDTH) + "║")
    print("║" + pad_line(f"    Total Likes:     {stats["like_count"]}", WIDTH) + "║")
    print("║" + pad_line(f"    Total Follows:   {stats["follow_count"]}", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")
    
    print("╠" + "═" * WIDTH + "╣")
    print("║" + pad_line("  ADMIN COMMANDS", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")

    commands = [
        "admin                              -> View platform statistics",
        "admin ban <username> [reason]      -> Ban a user",
        "admin unban <username>             -> Unban a user",
        "admin deletepost <post_id>         -> Delete a post",
        "admin makeadmin <username>         -> Grant admin privileges to a user",
        "admin removeadmin <username>       -> Revoke admin privileges from a user",
        "admin verify <username>            -> Verify a user",
        "admin unverify <username>          -> Unverify a user",
        "admin logs [<page>]                -> View admin logs"
    ]

    for command in commands:
        print("║" + pad_line(f"    {command}", WIDTH) + "║")
    print("╚" + "═" * WIDTH + "╝")


def print_admin_logs(page):
    if not auth.is_admin():
        return
    
    success, logs = get_admin_logs(page)

    if not success:
        print_warning(f"Error: {logs}")
        return

    if not logs:
        print_warning("No admin logs found.")
        return
    
    print(f"\n Admin Logs (Page {page}):")
    
    for log in logs:
        timestamp = format_timestamp(log["created"])
        print(f"\n    [{timestamp}] Admin @{log['admin_username']} performed action: {log['action']}")

        if log["details"]:
            print(f"        Details: {log['details']}")

    print_separator()    
    