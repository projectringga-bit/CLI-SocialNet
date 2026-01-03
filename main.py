import os
import sys
import getpass

import db
import auth
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
""")


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


    elif command == "whoami": # TODO: dedicated status function
        if auth.is_logged():
            user = auth.get_current_user()
            print_info(f"Currently logged in as: @{user['username']}")

        else:
            print_info("No user is currently logged in. Use 'login' or 'register' to continue.")

    
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


    else:
        print_error(f"Unknown command: {command}")
        print_info("Type 'help' to see the list of available commands.")

    return True


def show_home():
    clear()
    print_banner()

    if auth.is_logged():
        print("\n Your Feed (WIP)")

        print_separator()
        # TODO: show feed
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
            if auth.is_logged(): # TODO: verify session
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
