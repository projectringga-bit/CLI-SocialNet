import os
import sys
import getpass

import db
import auth
import posts
import social
import admin
from utils import print_success, print_error, print_warning, print_info, print_separator, print_banner, print_post, print_comment
from utils import clear


def help_message():
    print("""
Available commands:

help                             -> Show this help message
exit, quit                       -> Exit the application
clear                            -> Clear the console
register <username>              -> Register a new user
login <username>                 -> Login
logout                           -> Logout the current user
whoami                           -> Show the currently logged in user
deleteaccount                    -> Delete the currently logged in user's account
changepassword                   -> Change the password of the currently logged in user
home                             -> Show the home feed
feed [<page>]                    -> View your feed (posts from people you follow)
explore [<page>]                 -> View the global feed
post <content>                   -> Create a new post
postimg <image_path> [<caption>] -> Create a new post with an image from a local path
posturl <image_url> [<caption>]  -> Create a new post with an image from a URL
viewpost <post_id>               -> View a specific post
deletepost <post_id>             -> Delete a specific post
myposts                          -> View your own posts
displayname <new_display_name>   -> Change your display name
like <post_id>                   -> Like a post
unlike <post_id>                 -> Unlike a post
likes <post_id>                  -> View likes on a post
comment <post_id> <comment_text>  -> Comment on a post
delcomment <comment_id>          -> Delete a comment
comments <post_id>               -> View comments on a post
follow <username>                -> Follow a user
unfollow <username>              -> Unfollow a user
followers [<username>]           -> View followers of a user (or yourself if no username is provided)
following [<username>]           -> View users followed by a user (or yourself if no username is provided)
bio <new_bio>                    -> Change your bio
status <new_status>              -> Change your status
location <new_location>          -> Change your location
website <new_website>            -> Change your website
avatar <image_path>              -> Change your avatar using a local image path
avatarurl <image_url>            -> Change your avatar using an image URL
removeavatar                     -> Remove your avatar
profile [<username>]             -> View a user's profile (or your own if no username is provided)
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


    elif command == "feed":
        page = 1

        if not auth.is_logged():
            print_warning("You must be logged in to view your feed.")
            return True

        if len(args) > 1:
            print_error("Usage: feed [<page>]")
            return True

        if len(args) == 1:
            try:
                page = int(args[0])
            except ValueError:
                print_error("Page must be a number.")
                return True
            
        postss = posts.get_feed(page=page)

        if not postss:
            print_info("No posts to show.")
            return True

        posts.display_multiple_posts(postss, f"Your Feed - Page {page}")

    
    elif command == "explore":
        page = 1

        if len(args) > 1:
            print_error("Usage: explore [<page>]")
            return True
        
        if len(args) == 1:
            try:
                page = int(args[0])
            except ValueError:
                print_error("Page must be a number.")
                return True
            
        postss = posts.get_global_feed(page=page)

        if not postss:
            print_info("No posts to show.")
            return True

        posts.display_multiple_posts(postss, f"Explore - Page {page}")
    

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


    elif command == "postimg":
        if not auth.is_logged():
            print_warning("You must be logged in to create a post.")
            return True
        
        if len(args) == 0:
            print_error("Usage: postimg <image_path> [<caption>]")
            return True
        
        image_path = args[0]

        content = ""

        if len(args) > 1:
            content = " ".join(args[1:])

        success, message = posts.create_post(content, image_path=image_path)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "posturl":
        if not auth.is_logged():
            print_warning("You must be logged in to create a post.")
            return True
        
        if len(args) > 2:
            print_error("Usage: posturl <image_url> [<caption>]")
            return True
        
        image_url = args[0]

        content = ""

        if len(args) > 1:
            content = " ".join(args[1:])

        success, message = posts.create_post(content, image_url=image_url)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "viewpost":        
        if len(args) != 1:
            print_error("Usage: viewpost <post_id>")
            return True
        
        try:
            post_id = int(args[0])

        except ValueError:
            print_error("Post ID must be a number.")
            return True
        
        success, message = posts.display_single_post(post_id)

        if not success:
            print_error(message)


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
        page = 1

        if not auth.is_logged():
            print_warning("You must be logged in to view your posts.")
            return True
        
        if len(args) > 1:
            print_error("Usage: myposts [<page>]")
            return True
        
        if len(args) == 1:
            try:
                page = int(args[0])

            except ValueError:
                print_error("Page must be a number.")
                return True
        
        user = auth.get_current_user()

        my_posts = posts.get_my_posts(user['id'], page=page)

        success, message = posts.display_multiple_posts(my_posts, f"@{user['username']}'s Posts")

        if success:
            pass
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


    elif command == "comment":
        if not auth.is_logged():
            print_warning("You must be logged in to comment on a post.")
            return True
        
        if len(args) < 2:
            print_error("Usage: comment <post_id> <comment_text>")
            return True
        
        post_id = args[0]

        text = " ".join(args[1:])

        success, message = posts.comment(post_id, text)

        if success:
            print_success(message)
        else:
            print_error(message)

    
    elif command == "delcomment":
        if not auth.is_logged():
            print_warning("You must be logged in to delete a comment.")
            return True
        
        if len(args) != 1:
            print_error("Usage: delcomment <comment_id>")
            return True
        
        comment_id = args[0]

        success, message = posts.delete_comment(comment_id)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "comments":
        if len(args) != 1:
            print_error("Usage: comments <post_id>")
            return True
        
        post_id = args[0]

        success, comments = posts.get_post_comments(post_id)
        if not success:
            print_error(comments)
            return True
        
        if comments:
            print(f"\nComments on post #{post_id}:")
            
            for comment in comments:
                print_comment(comment)

            print_separator()

        else:
            print_info("No comments on this post yet.")


    elif command == "follow":
        if not auth.is_logged():
            print_warning("You must be logged in to follow a user.")
            return True
        
        if len(args) != 1:
            print_error("Usage: follow <username>")
            return True
        
        username = args[0].lstrip('@')

        success, message = social.follow(username)

        if success:
            print_success(f"You are now following @{username}.")
        else:
            print_error(message)


    elif command == "unfollow":
        if not auth.is_logged():
            print_warning("You must be logged in to unfollow a user.")
            return True
        
        if len(args) != 1:
            print_error("Usage: unfollow <username>")
            return True
        
        username = args[0].lstrip('@')

        success, message = social.unfollow(username)

        if success:
            print_success(f"You have unfollowed @{username}.")
        else:
            print_error(message)

    
    elif command == "followers":
        if not auth.is_logged():
            print_warning("You must be logged in to view followers.")
            return True
        
        if len(args) > 1:
            print_error("Usage: followers [<username>]")
            return True
        
        elif len(args) == 1:
            username = args[0].lstrip('@')
        
        else:
            username = None
            
        success, followers = social.display_followers(username)

        if success:
            print("\nFollowers:")
            for user in followers:
                print(f"    - {user}")
        else:
            print_info(followers)


    elif command == "following":
        if not auth.is_logged():
            print_warning("You must be logged in to view following users.")
            return True
        
        if len(args) > 1:
            print_error("Usage: following [<username>]")
            return True
        
        elif len(args) == 1:
            username = args[0].lstrip('@')

        else:
            username = None

        success, following = social.display_following(username)

        if success:
            print("\nFollowing:")
            for user in following:
                print(f"    - {user}")

        else:
            print_info(following)


    elif command == "profile":
        if not auth.is_logged():
            print_warning("You must be logged in to view profiles.")
            return True
        
        if len(args) > 1:
            print_error("Usage: profile [<username>]")
            return True
        
        elif len(args) == 1:
            username = args[0].lstrip('@')

        else:
            username = None

        success, follow_status = social.display_profile(username)

        if success:
            if follow_status != None:
                print_info(follow_status)

        else:
            print_error(follow_status)

        
    elif command == "displayname":
        if not auth.is_logged():
            print_warning("You must be logged in to change your display name.")
            return True
        
        if not args:
            print_error("Usage: displayname <new_display_name>")
            return True
        
        new_display_name = " ".join(args)

        success, message = social.update_display_name(new_display_name)

        if success:
            print_success(message)
        else:
            print_error(message)

    elif command == "bio":
        if not auth.is_logged():
            print_warning("You must be logged in to change your bio.")
            return True
        
        if not args:
            print_error("Usage: bio <new_bio>")
            return True
        
        new_bio = " ".join(args)

        success, message = social.update_bio(new_bio)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "status":
        if not auth.is_logged():
            print_warning("You must be logged in to change your status.")
            return True
        
        if not args:
            print_error("Usage: status <new_status>")
            return True
        
        new_status = " ".join(args)

        success, message = social.update_status(new_status)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "location":
        if not auth.is_logged():
            print_warning("You must be logged in to change your location.")
            return True
        
        if not args:
            print_error("Usage: location <new_location>")
            return True
        
        new_location = " ".join(args)

        success, message = social.update_location(new_location)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "website":
        if not auth.is_logged():
            print_warning("You must be logged in to change your website.")
            return True
        
        if not args:
            print_error("Usage: website <new_website>")
            return True
        
        new_website = " ".join(args)

        success, message = social.update_website(new_website)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "avatar":
        if not auth.is_logged():
            print_warning("You must be logged in to change your avatar.")
            return True
        
        if len(args) != 1:
            print_error("Usage: avatar <image_path>")
            return True
        
        image_path = args[0]

        success, message = social.update_avatar(avatar_path=image_path)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "avatarurl":
        if not auth.is_logged():
            print_warning("You must be logged in to change your avatar.")
            return True
        
        if len(args) != 1:
            print_error("Usage: avatarurl <image_url>")
            return True
        
        image_url = args[0]

        success, message = social.update_avatar(avatar_url=image_url)

        if success:
            print_success(message)
        else:
            print_error(message)


    elif command == "removeavatar":
        if not auth.is_logged():
            print_warning("You must be logged in to remove your avatar.")
            return True
        
        if len(args) != 0:
            print_error("Usage: removeavatar")
            return True

        success, message = social.remove_avatar()

        if success:
            print_success(message)
        else:
            print_error(message)


    # Admin commands
    elif command == "admin":
        if not auth.is_logged() or not auth.is_admin():
            print_warning("You must be logged in as an admin to use admin commands.")
            return True
        
        if len(args) == 0:
            admin.print_banner_admin()
            return True
        
        subcommand = args[0].lower()
        args = args[1:]


        if subcommand == "ban":
            if len(args) < 1:
                print_error("Usage: admin ban <username> [reason]")
                return True
            
            username = args[0].lstrip('@')

            reason = " ".join(args[1:])

            success, message = admin.ban_user(username, reason)

            if success:
                print_success(message)
            else:
                print_error(message)

        elif subcommand == "unban":
            if len(args) != 1:
                print_error("Usage: admin unban <username>")
                return True
            
            username = args[0].lstrip('@')

            success, message = admin.unban_user(username)

            if success:
                print_success(message)
            else:
                print_error(message)

        elif subcommand == "deletepost":
            if len(args) != 1:
                print_error("Usage: admin deletepost <post_id>")
                return True
            
            post_id = args[0]

            success, message = admin.delete_post(post_id)

            if success:
                print_success(message)
            else:
                print_error(message)
        
        elif subcommand == "makeadmin":
            if len(args) != 1:
                print_error("Usage: admin makeadmin <username>")
                return True
            
            username = args[0].lstrip('@')

            success, message = admin.make_admin(username)

            if success:
                print_success(message)
            else:
                print_error(message)

        elif subcommand == "removeadmin":
            if len(args) != 1:
                print_error("Usage: admin removeadmin <username>")
                return True
            
            username = args[0].lstrip('@')

            success, message = admin.remove_admin(username)

            if success:
                print_success(message)
            else:
                print_error(message)

        elif subcommand == "verify":
            if len(args) != 1:
                print_error("Usage: admin verify <username>")
                return True
            
            username = args[0].lstrip('@')

            success, message = admin.verify_user(username)

            if success:
                print_success(message)
            else:
                print_error(message)

        elif subcommand == "unverify":
            if len(args) != 1:
                print_error("Usage: admin unverify <username>")
                return True
            
            username = args[0].lstrip('@')

            success, message = admin.unverify_user(username)

            if success:
                print_success(message)
            else:
                print_error(message)

        elif subcommand == "logs":
            page = 1

            if len(args) > 1:
                print_error("Usage: admin logs [<page>]")
                return True
            
            if len(args) == 1:
                try:
                    page = int(args[0])

                except ValueError:
                    print_error("Page must be a number.")
                    return True
                
            admin.print_admin_logs(page=page)

        else:
            print_error(f"Unknown admin command: {subcommand}")
            print_info("Type 'admin' to see available commands.")


    else:
        print_error(f"Unknown command: {command}")
        print_info("Type 'help' to see the list of available commands.")

    return True


def show_home():
    clear()
    print_banner()

    if auth.is_logged():
        print("\n Your Feed (latest posts from people you follow)")

        print_separator()

        feed_posts = posts.get_feed()
        if feed_posts:
            for post in feed_posts[:5]:
                    print_post(post)

        else:
            print_info("Your feed is empty. Follow some users to see their posts here.")
        
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
            if auth.is_logged():
                user = auth.get_current_user()
                prompt = f"\n@{user['username']}> "
            else:
                prompt = "\nsocialnet> "
        
            command = input(prompt).strip()
            if not command:
                continue

            command, args = parse_command(command)

            if auth.is_logged() and not auth.validate_session():
                print_warning("Your session has expired. Please log in again.")
                continue

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
