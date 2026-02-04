import hashlib
import secrets
import re
import os
import sys
import time
import datetime
import unicodedata


COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "gray": "\033[90m",
    "white": "\033[0m"
}
def get_color_code(color_name):
    return COLORS.get(color_name, COLORS["white"])


WIDTH_Global = 80
def get_terminal_width():
    import auth, db

    if auth.is_logged():
        user = auth.get_current_user()
        settings = db.get_user_settings(user["id"])
        terminal_width = settings.get("terminal_width", WIDTH_Global)
    
    else:
        terminal_width = WIDTH_Global

    return terminal_width


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(32)
            
    pass_salt = password + salt
    hash = hashlib.sha256(pass_salt.encode()).hexdigest()

    return hash, salt


def verify_password(password, hashed_password, salt):
    new_hash, _ = hash_password(password, salt)
    if new_hash == hashed_password:
        return True
    
    return False


def generate_token():
    token = secrets.token_hex(32)
    return token


def validate_username(username):
    if not username:
        return False, "Username cannot be empty."

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if len(username) > 20:
        return False, "Username cannot be longer than 20 characters."

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."

    return True, ""


def validate_password(password):
    if not password:
        return False, "Password cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    return True, ""


def print_success(message):
    print(f"\033[92m ✓ {message}\033[0m")  # green

def print_error(message):
    print(f"\033[91m ✗ {message}\033[0m")  # red

def print_warning(message):
    print(f"\033[93m ⚠ {message}\033[0m")  # yellow

def print_info(message):
    print(f"\033[94m i {message}\033[0m")  # blue

def print_separator():
    print("\033[90m" + "-" * (get_terminal_width()+2) + "\033[0m")  # gray


def print_banner(color="cyan"):
    banner = r"""
 ██████╗██╗     ██╗    ███████╗ ██████╗  ██████╗██╗ █████╗ ██╗     ███╗   ██╗███████╗████████╗
██╔════╝██║     ██║    ██╔════╝██╔═══██╗██╔════╝██║██╔══██╗██║     ████╗  ██║██╔════╝╚══██╔══╝
██║     ██║     ██║    ███████╗██║   ██║██║     ██║███████║██║     ██╔██╗ ██║█████╗     ██║   
██║     ██║     ██║    ╚════██║██║   ██║██║     ██║██╔══██║██║     ██║╚██╗██║██╔══╝     ██║   
╚██████╗███████╗██║    ███████║╚██████╔╝╚██████╗██║██║  ██║███████╗██║ ╚████║███████╗   ██║   
 ╚═════╝╚══════╝╚═╝    ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝   ╚═╝   
 ______              _           __  ____         _      __  _  __    __                  __     
/_  __/__ ______ _  (_)__  ___ _/ / / __/__  ____(_)__ _/ / / |/ /__ / /__    _____  ____/ /__   
 / / / -_) __/  ' \/ / _ \/ _ `/ / _\ \/ _ \/ __/ / _ `/ / /    / -_) __/ |/|/ / _ \/ __/  '_/   
/_/  \__/_/ /_/_/_/_/_//_/\_,_/_/ /___/\___/\__/_/\_,_/_/ /_/|_/\__/\__/|__,__/\___/_/ /_/\_\    
                                                                                                 
    """
    print(get_color_code(color) + banner + get_color_code("white"))


def clear():
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")


def timestamp():
    timestamp = int(time.time())
    return timestamp


def format_timestamp(timestamp):
    if timestamp is None:
        return "unknown time"
    
    date_time = datetime.datetime.fromtimestamp(timestamp)
    now = datetime.datetime.now()

    difference = now - date_time

    if difference.days == 0:
        if difference.seconds < 60:
            return "just now"
        
        elif difference.seconds < 3600:
            minutes = difference.seconds // 60
            return f"{minutes} minute(s) ago"
        
        else:
            hours = difference.seconds // 3600
            return f"{hours} hour(s) ago"
        
    elif difference.days == 1:
        return "yesterday"
    
    elif difference.days < 7:
        return f"{difference.days} day(s) ago"
    
    else:
        return date_time.strftime("%Y-%m-%d")
    

def visible_width(text):
    width = 0

    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1

    return width

def pad_line(text, width):
    visible_length = visible_width(text)

    padding = width - visible_length

    if padding < 0:
        result = ""
        current_length = 0

        for char in text:
            if unicodedata.east_asian_width(char) in ('F', 'W'):
                char_length = 2
            else:
                char_length = 1

            if current_length + char_length > width:
                break

            result += char
            current_length += char_length
            
        return result

    return text + " " * padding


def wrap_text(text, content_with_lines):
    lines = []

    for texts in text.split("\n"):
        current_line = ""
        current_width = 0

        for word in texts.split(" "):
            word_width = visible_width(word)

            if current_width == 0:
                if word_width > content_with_lines:
                    while visible_width(word) > content_with_lines:
                        part = ""
                        part_width = 0

                        for char in word:
                            if unicodedata.east_asian_width(char) in ('F', 'W'):
                                char_length = 2
                            else:
                                char_length = 1

                            if (part_width + char_length) > content_with_lines:
                                break

                            part += char
                            part_width += char_length

                        lines.append(part)
                        word = word[len(part):]

                    if word:
                        current_line = word
                        current_width = visible_width(current_line)
                    
                else:
                    current_line = word
                    current_width = word_width
                
            elif (current_width + word_width + 1) <= content_with_lines:
                current_line += " " + word
                current_width += word_width + 1

            else:
                lines.append(current_line)

                if word_width > content_with_lines:
                    while visible_width(word) > content_with_lines:
                        part = ""
                        part_width = 0

                        for char in word:
                            if unicodedata.east_asian_width(char) in ('F', 'W'):
                                char_length = 2
                            else:
                                char_length = 1

                            if (part_width + char_length) > content_with_lines:
                                break

                            part += char
                            part_width += char_length

                        lines.append(part)
                        word = word[len(part):]

                    if word:
                        current_line = word
                        current_width = visible_width(current_line)

                    else:
                        current_line = ""
                        current_width = 0

                else:
                    current_line = word
                    current_width = word_width
            
        if current_line:
            lines.append(current_line)
            
        elif not lines:
            lines.append("")
        
    return lines


def print_post(data):
    import db
    import auth

    post_id = data.get("id", "")
    username = data.get("username", "unknown")
    display_name = data.get("display_name", "")
    content = data.get("content", "")
    created_at = data.get("created", None)
    likes_count = data.get("like_count", 0)
    comments_count = data.get("comment_count", 0)
    reposts_count = data.get("repost_count", 0)
    image_ascii = data.get("image_ascii", None)
    is_repost = data.get("repost_id", None)
    quote_content = data.get("quote_content", None)
    reposting_user = data.get("repost_username", None)

    WIDTH = get_terminal_width()
    
    print("╭" + "─" * WIDTH + "╮")

    if is_repost:
        repost_l = f" [Repost] @{reposting_user} reposted"
        print("│" + pad_line(repost_l, WIDTH) + "│")

        if quote_content:
            print("│" + " " * WIDTH + "│")
            quote_lines = wrap_text(quote_content, WIDTH - 4)

            for line in quote_lines:
                padded_line = line + " " * (WIDTH - 4 - visible_width(line))
                print("│  " + padded_line + "  │")

            print("│" + " " * WIDTH + "│")
        
        print("├" + "─" * WIDTH + "┤")
    
    if display_name:
        name = f"{display_name} (@{username})"
    else:
        name = f"@{username}"

    time_string = format_timestamp(created_at)
    header = f"[#{post_id}] {name}"

    header_visible_line = visible_width(header)
    timestamp_visible_line = visible_width(time_string)
    available_space_for_time = WIDTH - header_visible_line - timestamp_visible_line - 1

    if available_space_for_time >= 0:
        header_line = header + " " * (available_space_for_time + 1) + time_string + " "
    
    else:
        max_header_length = WIDTH - timestamp_visible_line - 3
        truncated_header = ""
        truncated_width = 0

        for char in header:
            if unicodedata.east_asian_width(char) in ('F', 'W'):
                char_length = 2
            else:
                char_length = 1

            if truncated_width + char_length > max_header_length:
                break

            truncated_header += char
            truncated_width += char_length
        
        header_line = truncated_header + "..." + " " + time_string + " "

    print("│" + pad_line(header_line, WIDTH) + "│")    
    print("│" + " " * WIDTH + "│")

    content_with_lines = WIDTH - 4
    wrapped_content = wrap_text(content, content_with_lines)

    for line in wrapped_content:
        padded_line = line + " " * (content_with_lines - visible_width(line))
        print("│  " + padded_line + "  │")

    if image_ascii:
        print("│" + " " * WIDTH + "│")

        for line in image_ascii.split("\n"):
            if visible_width(line) > WIDTH:
                truncated_line = ""
                current_width = 0

                for char in line:
                    if unicodedata.east_asian_width(char) in ('F', 'W'):
                        char_length = 2
                    else:
                        char_length = 1

                    if current_width + char_length > WIDTH:
                        break

                    truncated_line += char
                    current_width += char_length

                line_width = visible_width(truncated_line)
                line_pad = (WIDTH - line_width) // 2
                
                print("│" + " " * line_pad + truncated_line + " " * (WIDTH - line_pad - line_width) + "│")
            else:
                line_width = visible_width(line)
                line_pad = (WIDTH - line_width) // 2
                print("│" + " " * line_pad + line + " " * (WIDTH - line_pad - line_width) + "│")

    print("│" + " " * WIDTH + "│")

    poll = db.get_poll_by_post_id(post_id)
    if poll:
        question_l = wrap_text(f" POLL: {poll["question"]}", WIDTH - 4)

        for line in question_l:
            print("│  " + pad_line(line, WIDTH - 4) + "  │")
        print("│" + " " * WIDTH + "│")

        user_vote = None
        if auth.is_logged():
            user = auth.get_current_user()
            user_vote = db.get_user_poll_vote(user["id"], poll["id"])

        total_votes = poll["total_votes"]

        for item, option in enumerate(poll["options"], start=1):
            vote_count = option["vote_count"]
            if total_votes > 0:
                percentage = (vote_count / total_votes) * 100
            else:
                percentage = 0

            filled_part = int((20 * percentage) // 100)
            bar = "[" + "█" * filled_part + "-" * (20 - filled_part) + "]"
            
            if user_vote == option["id"]:
                user_voted_one = "✓"
            else:
                user_voted_one = " "

            option_l = f"  {item}. [{user_voted_one}] {option["option_text"]}"
            print("│  " + pad_line(option_l, WIDTH - 4) + "  │")

            bar_l = f"     {bar} {vote_count} vote(s) ({percentage:.1f}%)"
            print("│  " + pad_line(bar_l, WIDTH - 4) + "  │")

        total_l = f"Total Votes: {total_votes}"
        print("│  " + pad_line(total_l, WIDTH - 4) + "  │")
        print("│" + " " * WIDTH + "│")

        if user_vote:
            voted_l = f"You voted for option #{item}."
            print("│  " + pad_line(voted_l, WIDTH - 4) + "  │")
            
        print("│" + " " * WIDTH + "│")

    statistics_line = f"  ❤️ {likes_count}   🔁 {reposts_count}   💬 {comments_count}  "
    print("│" + pad_line(statistics_line, WIDTH) + "│")

    print("╰" + "─" * WIDTH + "╯")


def print_profile(user, posts=None, pinned=None):
    username = user.get("username", "unknown")
    display_name = user.get("display_name", "")
    bio = user.get("bio", "No bio")
    status = user.get("status", "")
    location = user.get("location", "")
    website = user.get("website", "")
    created = user.get("created", None)
    followers_count = user.get("followers_count", 0)
    following_count = user.get("following_count", 0)
    posts_count = user.get("posts_count", 0)
    profile_ascii = user.get("profile_ascii", None)
    is_admin = user.get("is_admin", 0)
    is_verified = user.get("is_verified", 0)
    is_private = user.get("is_private", 0)

    WIDTH = get_terminal_width()
    
    icons = []
    
    if is_admin:
        icons.append("🛡️ Admin")
    if is_verified:
        icons.append("✓ Verified")
    if is_private:
        icons.append("🔒 Private")

    icons_line = ""
    
    if icons:
        icons_line = f" [{' • '.join(icons)}] "

    print("╭" + "─" * WIDTH + "╮")

    title_pad = (WIDTH - 9) // 2
    print("│" + " " * title_pad + " Profile " + " " * (WIDTH - title_pad - 9) + "│")
    
    print("├" + "─" * WIDTH + "┤")

    if profile_ascii:
        print("│" + " " * WIDTH + "│")

        for line in profile_ascii.split("\n"):

            if len(line) > WIDTH - 4:
                line = line[:WIDTH - 4]
            
            line_padded = (WIDTH - len(line)) // 2
            print("│" + " " * line_padded + line + " " * (WIDTH - line_padded - len(line)) + "│")

        print("├" + "─" * WIDTH + "┤")

    print("│" + " " * WIDTH + "│")

    if display_name:
        name_l = f"{display_name} (@{username})"
    
    else:
        name_l = f"@{username}"

    print("│" + pad_line(f"  {name_l}{icons_line}", WIDTH) + "│")
    
    if status:
        print(f"│" + " " * WIDTH + "│")

        status_l = f"   Status: {status} "
        if len(status_l) > WIDTH -2:
            status_l = status_l[:WIDTH - 5] + "..."
        
        print(f"│" + pad_line(status_l, WIDTH) + "│")

    print("│" + " " * WIDTH + "│")
    print("├" + "─" * WIDTH + "┤")

    print("│" + pad_line(f"  BIO", WIDTH) + "│")
    print("│" + " " * WIDTH + "│")

    bio_with_lines = WIDTH - 6
    words = bio.split("\n")
    lines = []
    current_line = ""
    for word in words:
        if len(word) > bio_with_lines:
            while len(word) > bio_with_lines:
                part = word[:bio_with_lines]
                lines.append(part)
                word = word[bio_with_lines:]

            if word:
                current_line = word
                
        else:
            current_line = word

        if current_line:
            lines.append(current_line)
            current_line = ""

    for line in lines[:4]:
        print("│" + pad_line(f"   {line}", WIDTH) + "│")
    
    print("│" + " " * WIDTH + "│")

    if location or website:
        print("├" + "─" * WIDTH + "┤")
        print("│" + pad_line(f"  INFO", WIDTH) + "│")
        print("│" + " " * WIDTH + "│")

        if location:
            location_l = f"   📍 Location: {location}"
            if len(location_l) > WIDTH - 2:
                location_l = location_l[:WIDTH - 5] + "..."
            
            print("│" + pad_line(location_l, WIDTH) + "│")
        
        if website:
            website_l = f"   🔗 Website: {website}"
            if len(website_l) > WIDTH - 2:
                website_l = website_l[:WIDTH - 5] + "..."
            
            print("│" + pad_line(website_l, WIDTH) + "│")

        print("│" + " " * WIDTH + "│")
    
    print("├" + "─" * WIDTH + "┤")
    print("│" + pad_line(f"  STATISTICS", WIDTH) + "│")
    print("│" + " " * WIDTH + "│")

    stats_l1 = f"  Posts: {posts_count}   Followers: {followers_count}   Following: {following_count}  "
    stats_l2 = f"  Joined: {format_timestamp(created)}  "

    print("│" + pad_line(stats_l1, WIDTH) + "│")
    print("│" + pad_line(stats_l2, WIDTH) + "│")
    print("│" + " " * WIDTH + "│")

    print("╰" + "─" * WIDTH + "╯")

    if user.get("is_following") and user.get("follows_you"):
        print("  [✔] You and this user follow each other")
        
    elif user.get("is_following"):
        print("  [✔] You are following this user")
    
    elif user.get("follows_you"):
        print("  [✔] This user is following you")

    
    if pinned:
        print()
        print("╭" + "─" * WIDTH + "╮")
        print("│" + " " * ((WIDTH - 14) // 2) + " PINNED POSTS " + " " * (WIDTH - ((WIDTH - 14) // 2) - 14) + "│")
        print("╰" + "─" * WIDTH + "╯")

        for post in pinned:
            print_post(post)
    
    if posts:
        print()
        print("╭" + "─" * WIDTH + "╮")
        print("│" + " " * ((WIDTH - 14) // 2) + " RECENT POSTS " + " " * (WIDTH - ((WIDTH - 14) // 2) - 14) + "│")
        print("╰" + "─" * WIDTH + "╯")

        for post in posts:
            print_post(post)


def print_comment(data):
    comment_id = data.get("id", "")
    username = data.get("username", "unknown")
    display_name = data.get("display_name", "")
    content = data.get("content", "")
    created = data.get("created", None)

    WIDTH = get_terminal_width() - (get_terminal_width() // 100 * 20)  # 25%

    def wrap_text(text, content_with_lines):
        lines = []

        for texts in text.split("\n"):
            current_line = ""
            current_width = 0

            for word in texts.split(" "):
                word_width = len(word)

                if current_width == 0:
                    if word_width > content_with_lines:
                        while len(word) > content_with_lines:
                            part = word[:content_with_lines]
                            lines.append(part)
                            word = word[content_with_lines:]

                        if word:
                            current_line = word
                            current_width = len(current_line)

                    else:
                        current_line = word
                        current_width = word_width

                elif (current_width + word_width + 1) <= content_with_lines:
                    current_line += " " + word
                    current_width += word_width + 1

                else:
                    lines.append(current_line)

                    if word_width > content_with_lines:
                        while len(word) > content_with_lines:
                            part = word[:content_with_lines]
                            lines.append(part)
                            word = word[content_with_lines:]

                        if word:
                            current_line = word
                            current_width = len(current_line)

                        else:
                            current_line = ""
                            current_width = 0

                    else:
                        current_line = word
                        current_width = word_width

            if current_line:
                lines.append(current_line)

            elif not lines:
                lines.append("")
            
        return lines
    

    print("  ┌" + "─" * WIDTH + "┐")

    if display_name:
        name = f"{display_name} (@{username})"
    else:
        name = f"@{username}"

    time_len = len(format_timestamp(created))
    header = f"[#{comment_id}] {name}"
    header_len = len(header)

    if header_len + time_len + 2 <= WIDTH:
        space = WIDTH - header_len - time_len - 1
        header_line = header + " " * space + format_timestamp(created) + " "

    else:
        header_line = header[:WIDTH - time_len - 3] + "... " + format_timestamp(created) + " "

    print("  │" + pad_line(header_line, WIDTH) + "│")
    print("  │" + " " * WIDTH + "│")

    content_with_lines = WIDTH - 4
    wrapped_content = wrap_text(content, content_with_lines)

    for line in wrapped_content:
        padded_line = line + " " * (content_with_lines - len(line))
        print("  │  " + padded_line + "  │")

    print("  │" + " " * WIDTH + "│")

    print("  └" + "─" * WIDTH + "┘")


def print_settings(settings):
    WIDTH = get_terminal_width()

    print()
    print("╔" + "═" * WIDTH + "╗")
    title_pad = (WIDTH - len(" USER SETTINGS ")) // 2
    print("║" + " " * title_pad + " USER SETTINGS " + " " * (WIDTH - len(" USER SETTINGS ") - title_pad) + "║")

    print("╠" + "═" * WIDTH + "╣")

    print("║" + pad_line("  Appearance", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")
    print("║" + pad_line(f"   banner_color: {settings.get('banner_color', 'cyan')}", WIDTH) + "║")
    print("║" + pad_line(f"   prompt_color: {settings.get('prompt_color', 'white')}", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")

    print("╠" + "═" * WIDTH + "╣")

    print("║" + pad_line("  Display", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")
    print("║" + pad_line(f"   posts_per_page: {settings.get('posts_per_page', 10)}", WIDTH) + "║")
    print("║" + pad_line(f"   terminal_width: {settings.get('terminal_width', 80)}", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")

    print("╠" + "═" * WIDTH + "╣")

    print("║" + pad_line("  Notifications", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")

    if settings.get("notify_on_follow", 1):
        follow_status = "Enabled"
    else:
        follow_status = "Disabled"
    print("║" + pad_line(f"   notify_on_follow: {follow_status}", WIDTH) + "║")
    
    if settings.get("notify_on_like", 1):
        like_status = "Enabled"
    else:
        like_status = "Disabled"
    print("║" + pad_line(f"   notify_on_like: {like_status}", WIDTH) + "║")
    
    if settings.get("notify_on_comment", 1):
        comment_status = "Enabled"
    else:
        comment_status = "Disabled"
    print("║" + pad_line(f"   notify_on_comment: {comment_status}", WIDTH) + "║")
    
    if settings.get("notify_on_repost", 1):
        repost_status = "Enabled"
    else:
        repost_status = "Disabled"
    print("║" + pad_line(f"   notify_on_repost: {repost_status}", WIDTH) + "║")
    
    if settings.get("notify_on_mention", 1):
        mention_status = "Enabled"
    else:
        mention_status = "Disabled"
    print("║" + pad_line(f"   notify_on_mention: {mention_status}", WIDTH) + "║")
    
    if settings.get("notify_on_dm", 1):
        dm_status = "Enabled"
    else:
        dm_status = "Disabled"
    print("║" + pad_line(f"   notify_on_dm: {dm_status}", WIDTH) + "║")
    print("║" + " " * WIDTH + "║")
    
    print("╠" + "═" * WIDTH + "╣")

    print("║" + pad_line(" Setting: 0 for Disabled, 1 for Enabled", WIDTH) + "║")    
    print("║" + pad_line(" Available colors: red, green, yellow, blue, magenta, cyan, white", WIDTH) + "║")
    print("║" + pad_line(" Changing the terminal_width may result in display issues...", WIDTH) + "║")

    print("╚" + "═" * WIDTH + "╝")
    print()
