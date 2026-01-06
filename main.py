import os
import sys
import getpass

import db
import auth
import posts
from utils import print_success, print_error, print_warning, print_info, print_separator, print_banner
from utils import clear


def help_message():
    print("""
Available commands:
help -> Show this help message
exit, quit -> Exit the application
clear -> Clear the console
register <username> -> Register a new user
login <username> -> Login
logout -> Logout the current user
whoami -> Show the currently logged in user
deleteaccount -> Delete the currently logged in user's account
changepassword -> Change the password of the currently logged in user
home -> Show the home feed
post <content> -> Create a new post
viewpost <post_id> -> View a specific post
deletepost <post_id> -> Delete a specific post
myposts -> View your own posts
displayname <new_display_name> -> Change your display name
like <post_id> -> Like a post
unlike <post_id> -> Unlike a post
likes <post_id> -> View likes on a post
follow <username> -> Follow a user
""")
    

def show_status():
    if auth.is_logged():
        user = auth.get_current_user()
        
        display_name = user.get("display_name")

        if display_name:
            print_info(f"Logged in as: {display_name} (@{user['username']})")
        else:
            print(f"Logged in as: @{user['username']}")
    
    else:
        print_info("No user is currently logged in. Use 'login' or 'register' to continue.")


def parse_command(input_command):
    parts = input_command.split()

    if not parts:
        return None, None
    
    command = parts[0].lower()
    args = parts[1:]

    return command, args


def execute_command(command, args): # returns True (continue) or False (exit)
    if command == "exit" or command == "quit":
        if auth.is_logged():
            auth.logout()

        print_info("Exiting...")
        return False


    elif command == "help":
        help_message()


    elif command == "clear":
        clear()
        print_banner()


    elif command == "home":
        show_home()

    
    elif command == "whoami":
        show_status()


    elif command == "register":
        if auth.is_logged():
            print_warning("You are already logged in.")
            return True
        
        if len(args) != 1:
            print_error("Usage: register <username>")
            return True

        username = args[0]

        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm Password: ")

        if password != password_confirm:
            print_error("Passwords do not match.")
            return True
        
        success, message = auth.register(username, password)
        
        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "login":
        if auth.is_logged():
            print_warning("You are already logged in.")
            return True
        
        if len(args) != 1:
            print_error("Usage: login <username>")
            return True

        username = args[0]
        password = getpass.getpass("Password: ")

        success, message = auth.login(username, password)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "logout":
        if not auth.is_logged():
            print_warning("No user is currently logged in.")
            return True

        success, message = auth.logout()

        if success:
            print_success(message)
        else:
            print_error(message)

    
    elif command == "deleteaccount":
        if not auth.is_logged():
            print_warning("No user is currently logged in.")
            return True
        
        if len(args) != 0:
            print_error("Usage: deleteaccount")
            return True
        
        confirm = input("Are you sure you want to delete your account? This action cannot be undone. (yes/no): ").strip().lower()
        if confirm == "yes":
            password = getpass.getpass("Enter your password to confirm: ")

            success, message = auth.delete_account(password)

            if success:
                print_success(message)
            else:
                print_error(message)
                
        else:
            print_info("Account deletion aborted.")
            return True
        

    elif command == "changepassword":
        if not auth.is_logged():
            print_warning("No user is currently logged in.")
            return True
        
        if len(args) != 0:
            print_error("Usage: changepassword")
            return True

        old_password = getpass.getpass("Current Password: ")
        new_password = getpass.getpass("New Password: ")
        new_password_confirm = getpass.getpass("Confirm New Password: ")

        if new_password != new_password_confirm:
            print_error("New passwords do not match.")
            return True
        
        success, message = auth.change_password(old_password, new_password)

        if success:
            print_success(message)
        else:
            print_error(message)

        
    elif command == "post":
        if not auth.is_logged():
            print_warning("You must be logged in to create a post.")
            return True
        
        if len(args) == 0:
            print_error("Usage: post <content>")
            return True
        
        content = " ".join(args)

        success, message = posts.create_post(content)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "viewpost":
        if not auth.is_logged():
            print_warning("You must be logged in to view a post.")
            return True
        
        if len(args) != 1:
            print_error("Usage: viewpost <post_id>")
            return True
        
        post_id = args[0]
        
        post = posts.view_post(post_id) # TODO: CHANGE THIS
        if post is None:
            print_error("Post not found.")
        else:
            user = auth.get_current_user() 
            print_separator()
            print(f"Post ID: {post['id']} by User ID: {post['user_id']}")
            print_separator()
            print("\n" + post["content"] + "\n")
            print_separator()


    elif command == "deletepost":
        if not auth.is_logged():
            print_warning("You must be logged in to delete a post.")
            return True
        
        if len(args) != 1:
            print_error("Usage: deletepost <post_id>")
            return True
        
        post_id = args[0]

        success, message = posts.delete_post(post_id)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "myposts":
        if not auth.is_logged():
            print_warning("You must be logged in to view your posts.")
            return True
        
        user = auth.get_current_user()

        my_posts = posts.view_user_posts(user["username"])

        for post in my_posts:
            print(f"Post ID: {post['id']}")
            print_separator()
            print("\n" + post["content"] + "\n")
            print_separator()


    elif command == "displayname":
        if not auth.is_logged():
            print_warning("You must be logged in to change your display name.")
            return True
        
        if not args:
            print_error("Usage: displayname <new_display_name>")
            return True
        
        new_display_name = " ".join(args)

        success, message = auth.change_display_name(new_display_name)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "like":
        if not auth.is_logged():
            print_warning("You must be logged in to like a post.")
            return True
        
        if len(args) != 1:
            print_error("Usage: like <post_id>")
            return True
        
        post_id = args[0]

        success, message = posts.like_post(post_id)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "unlike":
        if not auth.is_logged():
            print_warning("You must be logged in to unlike a post.")
            return True
        
        if len(args) != 1:
            print_error("Usage: unlike <post_id>")
            return True
        
        post_id = args[0]

        success, message = posts.unlike_post(post_id)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "likes":
        if not auth.is_logged():
            print_warning("You must be logged in to view likes on a post.")
            return True
        
        if len(args) != 1:
            print_error("Usage: likes <post_id>")
            return True
        
        post_id = args[0]

        likes, error = posts.get_likes(post_id)

        if error:
            print_error(error)
            return True

        if likes:
            print(f"\nLikes on post #{post_id}:")
            for like in likes:
                print(f"    - @{like['username']}")

        else:
            print_info("No likes on this post yet.")


    elif command == "follow":
        if not auth.is_logged():
            print_warning("You must be logged in to follow a user.")
            return True
        
        if len(args) != 1:
            print_error("Usage: follow <username>")
            return True
        
        username = args[0].lstrip('@')

        target = db.get_user_by_username(username)
        if target is None:
            print_error("User not found.")
            return True
        
        current_user = auth.get_current_user()
        
        success, message = db.follow_user(current_user["id"], target["id"])

        if success:
            print_success(f"You are now following @{username}.")
        else:
            print_error(message)


    else:
        print_error(f"Unknown command: {command}")
        print_info("Type 'help' to see the list of available commands.")

    return True


def show_home():
    clear()
    print_banner()

    if auth.is_logged():
        print("\n Your Feed")

        print_separator()

        feed_posts = posts.get_home_feed() # TODO: CHANGE THIS
        for post in feed_posts:
            print(f"Post ID: {post['id']} by User ID: {post['user_id']}")
            print_separator()
            print("\n" + post["content"] + "\n")
            print()
            likes, _ = posts.get_likes(post['id'])
            print(f"    Likes: {len(likes)} likes")
            print_separator()

        print_separator()

    else:
        print("Welcome to CLI-SocialNet!")
        print("Get started by registering or logging in.")


def main():
    print("Init database...")
    db.init_db()

    db.clean_expired_sessions()

    show_home()

    running = True
    while running:
        try:
            if auth.is_logged() and not auth.validate_session():
                print_warning("Your session has expired. Please log in again.")

            if auth.is_logged():
                user = auth.get_current_user()
                prompt = f"\n@{user['username']}> "
            else:
                prompt = "\nsocialnet> "
        
            command = input(prompt).strip()
            if not command:
                continue

            command, args = parse_command(command)

            if command:
                running = execute_command(command, args)
        
        except KeyboardInterrupt:
            print("\n")
            print_info("Use 'exit' or 'quit' to exit")

        except Exception as e:
            print_error(f"Error: {e}")
    
    db.close_db()
    print_info("Database connection closed. Goodbye!")

if __name__ == "__main__":
    main()
