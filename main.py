import os
import sys
import getpass

import db
import auth
from utils import clear


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

        return False


    elif command == "help":
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
""")


    elif command == "clear":
        clear()


    elif command == "register":
        if auth.is_logged():
            print("Warning: You are already logged in.")
            return True
        
        if len(args) != 1:
            print("Usage: register <username>")
            return True

        username = args[0]

        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm Password: ")

        if password != password_confirm:
            print("Error: Passwords do not match.")
            return True
        
        success, message = auth.register(username, password)
        
        print(message)


    elif command == "login":
        if auth.is_logged():
            print("Warning: You are already logged in.")
            return True
        
        if len(args) != 1:
            print("Usage: login <username>")
            return True

        username = args[0]
        password = getpass.getpass("Password: ")

        success, message = auth.login(username, password)

        print(message)


    elif command == "logout":
        if not auth.is_logged():
            print("Warning: No user is currently logged in.")
            return True

        success, message = auth.logout()

        print(message)


    elif command == "whoami":
        if auth.is_logged():
            user = auth.get_current_user()
            print(f"Currently logged in as: @{user['username']}")

        else:
            print("No user is currently logged in. Use 'login' or 'register' to continue.")

    
    elif command == "deleteaccount":
        if not auth.is_logged():
            print("Warning: No user is currently logged in.")
            return True
        
        if len(args) != 0:
            print("Usage: deleteaccount")
            return True
        
        confirm = input("Are you sure you want to delete your account? This action cannot be undone. (yes/no): ").strip().lower()
        if confirm == "yes":
            password = getpass.getpass("Enter your password to confirm: ")

            success, message = auth.delete_account(password)

            print(message)
                
        else:
            print("Account deletion aborted.")
            return True
        

    elif command == "changepassword":
        if not auth.is_logged():
            print("Warning: No user is currently logged in.")
            return True
        
        if len(args) != 0:
            print("Usage: changepassword")
            return True

        old_password = getpass.getpass("Current Password: ")
        new_password = getpass.getpass("New Password: ")
        new_password_confirm = getpass.getpass("Confirm New Password: ")

        if new_password != new_password_confirm:
            print("Error: New passwords do not match.")
            return True
        
        success, message = auth.change_password(old_password, new_password)

        print(message)


    else:
        print(f"Unknown command: {command}")

    return True


def main():
    print("Init database...")
    db.init_db()

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

            if command:
                running = execute_command(command, args)
        
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'quit' to exit")

        except Exception as e:
            print(f"Error: {e}")
    
    db.close_db()
    print("Database connection closed. Goodbye!")

if __name__ == "__main__":
    main()
