import os
import threading
import asyncio
import time
from bot.painter import painters
from bot.mineclaimer import mine_claimer
from bot.utils import Colors
from bot.notpx import NotPx
from telethon.sync import TelegramClient
from datetime import datetime

# Removed the Bot Token, Admin Chat ID, and License Key System
# File structure for sessions
SESSIONS_DIR = "sessions/"

# Function to list available sessions
def show_sessions():
    if not os.path.exists(SESSIONS_DIR):
        os.mkdir(SESSIONS_DIR)
    sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")]
    if not sessions:
        print("[!] No sessions found.")
    else:
        print("Available sessions:")
        for i, session in enumerate(sessions, 1):
            print(f"{i}. {session[:-8]}")  # Display session name without .session extension

def add_api_credentials():
    api_id = input("Enter API ID: ")
    api_hash = input("Enter API Hash: ")
    env_path = os.path.join(os.path.dirname(__file__), 'env.txt')
    with open(env_path, "w") as f:
        f.write(f"API_ID={api_id}\n")
        f.write(f"API_HASH={api_hash}\n")
    print("[+] API credentials saved successfully in env.txt file.")

def reset_api_credentials():
    env_path = os.path.join(os.path.dirname(__file__), 'env.txt')
    if os.path.exists(env_path):
        os.remove(env_path)
        print("[+] API credentials reset successfully.")
    else:
        print("[!] No env.txt file found. Nothing to reset.")

def reset_session():
    if not os.path.exists(SESSIONS_DIR):
        os.mkdir(SESSIONS_DIR)
    sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")]
    if not sessions:
        print("[!] No sessions found.")
        return
    print("Available sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session[:-8]}")
    choice = input("Enter the number of the session to reset: ")
    try:
        session_to_reset = sessions[int(choice) - 1]
        os.remove(os.path.join(SESSIONS_DIR, session_to_reset))
        print(f"[+] Session {session_to_reset[:-8]} reset successfully.")
    except (ValueError, IndexError):
        print("[!] Invalid choice. Please try again.")

def load_api_credentials():
    env_path = os.path.join(os.path.dirname(__file__), 'env.txt')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
            api_id = None
            api_hash = None
            for line in lines:
                if line.startswith('API_ID='):
                    api_id = line.split('=')[1].strip()
                elif line.startswith('API_HASH='):
                    api_hash = line.split('=')[1].strip()
            return api_id, api_hash
    return None, None

def multithread_starter():
    print("Starting script...")
    if not os.path.exists(SESSIONS_DIR):
        os.mkdir(SESSIONS_DIR)
    dirs = os.listdir(SESSIONS_DIR)
    sessions = list(filter(lambda x: x.endswith(".session"), dirs))
    sessions = list(map(lambda x: x.split(".session")[0], sessions))

    for session_name in sessions:
        try:
            cli = NotPx(SESSIONS_DIR + session_name)

            def run_painters():
                asyncio.run(painters(cli, session_name))

            def run_mine_claimer():
                asyncio.run(mine_claimer(cli, session_name))

            threading.Thread(target=run_painters).start()
            threading.Thread(target=run_mine_claimer).start()
        except Exception as e:
            print(f"[!] Error loading session '{session_name}', error: {e}")

def process():
    print(r"""{}
███████  █████  ██    ██  █████  ███    ██ 
██      ██   ██ ██    ██ ██   ██ ████   ██ 
███████ ███████ ██    ██ ███████ ██ ██  ██ 
     ██ ██   ██  ██  ██  ██   ██ ██  ██ ██ 
███████ ██   ██   ████   ██   ██ ██   ████ 
                                                
            NotPx Auto Paint & Claim by @sgr - v1.0 {}""".format(Colors.BLUE, Colors.END))
    
    while True:
        print("\nMain Menu:")
        print("1. Add Account Session")
        print("2. Start Mine + Claim")
        print("3. Add API ID and Hash")
        print("4. Reset API Credentials")
        print("5. Reset Session")
        print("6. Show Available Sessions")
        print("7. Exit")
        
        option = input("Enter your choice: ")

        if option == "1":
            name = input("\nEnter Session name: ")
            if not os.path.exists(SESSIONS_DIR):
                os.mkdir(SESSIONS_DIR)
            if not any(name in i for i in os.listdir(SESSIONS_DIR)):
                api_id, api_hash = load_api_credentials()
                if api_id and api_hash:
                    client = TelegramClient(SESSIONS_DIR + name, api_id, api_hash).start()
                    client.disconnect()
                    print(f"[+] Session '{name}' saved successfully.")
                else:
                    print("[!] API credentials not found. Please add them first.")
            else:
                print(f"[x] Session '{name}' already exists.")
        elif option == "2":
            multithread_starter()
        elif option == "3":
            add_api_credentials()
        elif option == "4":
            reset_api_credentials()
        elif option == "5":
            reset_session()
        elif option == "6":
            show_sessions()
        elif option == "7":
            print("Exiting...")
            break
        else:
            print("[!] Invalid option. Please try again.")

if __name__ == "__main__":
    if not os.path.exists(SESSIONS_DIR):
        os.mkdir(SESSIONS_DIR)
    process()
    
