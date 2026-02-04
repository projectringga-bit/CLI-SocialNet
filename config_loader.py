import json
import os
import sys

DEFAULT_CONFIG = {
    "DATABASE": "sqlite",
    "SQL_PATH": "socialnet.db",
    "MONGODB_URI": "mongodb://localhost:27017/",
    "MONGODB_NAME": "socialnet",
    "ENABLE_REGISTRATION_LIMIT": True,
    "DEFAULT_ADMIN_PASSWORD": "admin123"
}

def load_config():
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(path, 'config.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                return config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration.")
            return DEFAULT_CONFIG.copy()
        
    else:
        print("No config file found. Creating default config.json.")
        try:
            with open(config_path, 'w') as config_file:
                json.dump(DEFAULT_CONFIG, config_file, indent=4)
            print("Default config.json created.")

        except Exception as e:
            print(f"Error creating default config: {e}")
        
        return DEFAULT_CONFIG.copy()
    
config = load_config()
DATABASE = config.get("DATABASE")
SQL_PATH = config.get("SQL_PATH")
MONGODB_URI = config.get("MONGODB_URI")
MONGODB_NAME = config.get("MONGODB_NAME")
ENABLE_REGISTRATION_LIMIT = config.get("ENABLE_REGISTRATION_LIMIT")
DEFAULT_ADMIN_PASSWORD = config.get("DEFAULT_ADMIN_PASSWORD")
