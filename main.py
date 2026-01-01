import sys

import db
import re
import hashlib
import secrets
import getpass

current_user = None

def parse_command(input_command):
    parts = input_command.split()

    if not parts:
        return None, None
    
    command = parts[0].lower()
    args = parts[1:]

    return command, args

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

def execute_command(command, args): # returns True (continue) or False (exit)
    if command == "exit" or command == "quit":
        return False
    
    elif command == "help":
        print("""
Available commands:
help -> Show this help message
exit, quit -> Exit the application
register <username> -> Register a new user
login <username> -> Login
""")
    
    elif command == "register":
        if len(args) != 1:
            print("Usage: register <username>")
            return True
        
        username = args[0]

        if not username:
            print("Username cannot be empty.")
            return True
        
        if len(username) < 3:
            print("Username must be at least 3 characters long.")
            return True
        
        if len(username) > 20:
            print("Username cannot be longer than 20 characters.")
            return True
        
        if not re.match("^[a-zA-Z0-9_]+$", username):
            print("Username can only contain letters, numbers, and underscores.")
            return True
        
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm Password: ")
        
        if not password:
            print("Password cannot be empty.")
            return True
        
        if len(password) < 6:
            print("Password must be at least 6 characters long.")
            return True
        
        if password != password_confirm:
            print("Error: Passwords do not match.")
            return True
        
        db.create_user(username, password)
        print(f"User '{username}' registered successfully.")


    elif command == "login":
        global current_user

        if len(args) != 1:
            print("Usage: login <username>")
            return True

        username = args[0]
        
        user = db.get_user_by_username(username)
        if user is None:
            print("Error: Invalid username")
            return True
        
        password = getpass.getpass("Password: ")
        
        if verify_password(password, user["password_hash"], user["password_salt"]):
            current_user = user
            print(f"User '{username}' logged in successfully.")
            return True
        
        else:
            print("Error: Invalid password")
            return True



    else:
        print(f"Unknown command: {command}.")

    return True


def main():
    print("Init database...")
    db.init_db()

    running = True
    while running:
        try:
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

if __name__ == "__main__":
    main()
