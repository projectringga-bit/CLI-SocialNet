import db
import auth
from utils import print_separator
from utils import timestamp

XP_GIVEN = {
    "post": 10,
    "comment": 5,
    "like": 2,
    "repost": 5,
    "follow": 5,
}

LEVELS = [0, 100, 250, 500, 1000, 2000, 4000, 8000, 10000, 15000, 20000, 26000, 34000, 42000, 50000, 60000, 75000, 90000, 110000, 130000]

ACHIEVEMENTS = [
    {
        "id": "first_post",
        "name": "First Post",
        "description": "Created your first post.",
        "xp": 50,
        "condition": lambda user_id: db.get_posts_count(user_id) >= 1
    },
    {
        "id": "first_follow",
        "name": "Social",
        "description": "Followed your first user.",
        "xp": 30,
        "condition": lambda user_id: db.get_following_count(user_id) >= 1
    },
    {
        "id": "poster",
        "name": "Poster",
        "description": "Created 10 posts.",
        "xp": 100,
        "condition": lambda user_id: db.get_posts_count(user_id) >= 10
    },
    {
        "id": "writer",
        "name": "Writer",
        "description": "Created 100 posts.",
        "xp": 1000,
        "condition": lambda user_id: db.get_posts_count(user_id) >= 100
    },
    {
        "id": "writer_pro",
        "name": "Writer Pro",
        "description": "Created 500 posts.",
        "xp": 5000,
        "condition": lambda user_id: db.get_posts_count(user_id) >= 500
    },
    {
        "id": "famous_lol",
        "name": "Famous lol",
        "description": "Get your first follower.",
        "xp": 30,
        "condition": lambda user_id: db.get_followers_count(user_id) >= 1
    },
    {
        "id": "influencer",
        "name": "Influencer",
        "description": "Get 100 followers.",
        "xp": 1000,
        "condition": lambda user_id: db.get_followers_count(user_id) >= 100
    },
    {
        "id": "celebrity",
        "name": "Celebrity",
        "description": "Get 1000 followers.",
        "xp": 5000,
        "condition": lambda user_id: db.get_followers_count(user_id) >= 1000
    },
    {
        "id": "liked",
        "name": "Liked",
        "description": "Receive your first like.",
        "xp": 20,
        "condition": lambda user_id: db.get_user_likes_count(user_id) >= 1
    },
    {
        "id": "popular",
        "name": "Popular",
        "description": "Receive 500 likes.",
        "xp": 2000,
        "condition": lambda user_id: db.get_user_likes_count(user_id) >= 500
    },
    {
        "id": "star",
        "name": "Star",
        "description": "Receive 5000 likes.",
        "xp": 10000,
        "condition": lambda user_id: db.get_user_likes_count(user_id) >= 5000
    }
]


def add_xp(user_id, amount):
    data = db.get_user_xp(user_id)
    current_xp = data["xp"]
    current_level = data["level"]

    new_xp = current_xp + amount
    new_level = current_level

    for item, to_level in enumerate(LEVELS):
        if new_xp >= to_level:
            new_level = item + 1

    db.update_user_xp(user_id, new_xp, new_level)

    is_level_up = new_level > current_level

    if is_level_up:
        message = f"\033[92mCongratulations! You've leveled up to Level {new_level}!\033[0m"
    else:
        message = None
    
    return is_level_up, message 


def check_achievements(user_id):
    unlocked_ids = db.get_achievements_id(user_id)
    new_unlock = []

    for achievement in ACHIEVEMENTS:
        if achievement["id"] not in unlocked_ids:
            if achievement["condition"](user_id):
                db.unlock_achievement(user_id, achievement["id"])
                
                add_xp(user_id, achievement["xp"])

                new_unlock.append(achievement)
            
    return new_unlock


def show_xp():
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    data = db.get_user_xp(user["id"])

    xp = data["xp"]
    level = data["level"]

    if level < len(LEVELS):
        current_level_xp = LEVELS[level-1]
        next_level_xp = LEVELS[level]
        xp_now = xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        percent = (xp_now / xp_needed) * 100

        print_separator()

        print(f"Level: {level}")
        print(f"XP: {xp} ({xp_needed-xp_now} to next level, {percent:.2f}%)")

        filled = int(30 * percent / 100)
        bar = "[" + "█" * filled + "-" * (30 - filled) + "]"
        print(bar)

        print_separator()

    else:
        print_separator()
        print(f"Level: {level} (MAX LEVEL)")
        print(f"XP: {xp} (You have reached the maximum level!)")
        print_separator()
    
    return True, None


def show_achievements():
    if not auth.is_logged():
        return False, "You must be logged in."
    
    user = auth.get_current_user()
    unlocked_ids = db.get_achievements_id(user["id"])

    achievements = []
    for achievement in ACHIEVEMENTS:
        achievements.append({
            "id": achievement["id"],
            "name": achievement["name"],
            "description": achievement["description"],
            "xp": achievement["xp"],
            "unlocked": achievement["id"] in unlocked_ids
        })
    
    count = 0
    for achievement in achievements:
        if achievement["unlocked"]:
            count += 1
        else:
            continue

    print()
    print(f"ACHIEVEMENTS ({count}/{len(achievements)} unlocked)")
    print_separator()

    for achievement in achievements:
        if achievement["unlocked"]:
            status = "UNLOCKED"
        else:
            status = "LOCKED"
        
        print(f" - {status} - {achievement['name']} (XP: {achievement['xp']})")
        print(f"     {achievement['description']}")
        print()

    print_separator()
    return True, None

def show_leaderboard(limit):
    leaderboard = db.get_leaderboard(limit)

    print()
    print(f"LEADERBOARD (Top {limit})")
    print_separator()

    for item, user in enumerate(leaderboard, start=1):
        print(f"{item}. @{user['username']} - Level {user['level']} (XP: {user['xp']})")
        print()

    print_separator()

    return True, None
