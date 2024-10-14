import os
import threading
import asyncio
import time
from bot.painter import painters  # Assuming bot.painter has the 'painters' function
from bot.mineclaimer import mine_claimer  # Assuming bot.mineclaimer has the 'mine_claimer' function
from bot.utils import Colors  # Assuming bot.utils has the 'Colors' class for colored output
from bot.notpx import NotPx  # Assuming bot.notpx has the 'NotPx' client implementation
from telethon.sync import TelegramClient  # Telethon client for Telegram interactions
from datetime import datetime
import sys

# File structure for sessions
SESSIONS_DIR = "sessions/"

# Function to manage printing and auto-removal of messages
def print_auto_remove(message, duration=15):
    sys.stdout.write(f"{message}\n")
    sys.stdout.flush()
    time.sleep(duration)
    sys.stdout.write("\r" + " " * len(message) + "\r")  # Clear the line
    sys.stdout.flush()

# Existing functions...

# Multithread starter for painters and mining
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

            previous_balance = None  # Track previous balance

            def run_painters():
                asyncio.run(painters(cli, session_name))

            def run_mine_claimer():
                nonlocal previous_balance
                while True:
                    # Simulating balance check (replace with actual logic)
                    current_balance = cli.get_balance(session_name)  # Assuming this function exists
                    if previous_balance is not None:
                        points_earned = current_balance - previous_balance
                        if points_earned > 0:
                            # Use the print_auto_remove function for the red message
                            threading.Thread(target=print_auto_remove, args=(f"[+] {session_name}: {points_earned} Pixel painted successfully.", 15)).start()
                            if points_earned >= 10:
                                print(f"BONUS! {points_earned}+ points earned!")
                    previous_balance = current_balance
                    time.sleep(3)  # Assuming the script checks every 3 seconds

            threading.Thread(target=run_painters).start()
            threading.Thread(target=run_mine_claimer).start()
        except Exception as e:
            print(f"[!] Error loading session '{session_name}', error: {e}")

# Main process function to handle menu interaction
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
                
