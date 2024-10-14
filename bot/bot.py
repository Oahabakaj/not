import os
import threading
import asyncio
import time
import sys
import nest_asyncio
from bot.painter import painters  # Assuming bot.painter has the 'painters' function
from bot.mineclaimer import mine_claimer  # Assuming bot.mineclaimer has the 'mine_claimer' function
from bot.utils import Colors  # Assuming bot.utils has the 'Colors' class for colored output
from bot.notpx import NotPx  # Assuming bot.notpx has the 'NotPx' client implementation
from telethon.sync import TelegramClient  # Telethon client for Telegram interactions
from datetime import datetime

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

SESSIONS_DIR = "sessions/"

# Function to manage printing and auto-removal of messages
def print_auto_remove(message, duration=15):
    sys.stdout.write(f"{message}\n")
    sys.stdout.flush()
    time.sleep(duration)
    sys.stdout.write("\r" + " " * len(message) + "\r")  # Clear the line
    sys.stdout.flush()

# Function to load API credentials from env.txt file
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

# Function to clear the console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear command for Windows and Unix-based systems

# Function to display text smoothly
def smooth_print(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Move to the next line after finishing

# Create new event loops for each async task
def run_async_in_thread(loop, coro):
    asyncio.set_event_loop(loop)  # Set this thread's event loop
    loop.run_until_complete(coro)

# Multithread starter for painters and mining
def multithread_starter():
    smooth_print(Colors.YELLOW + "Starting script..." + Colors.END)
    if not os.path.exists(SESSIONS_DIR):
        os.mkdir(SESSIONS_DIR)
    dirs = os.listdir(SESSIONS_DIR)
    sessions = list(filter(lambda x: x.endswith(".session"), dirs))
    sessions = list(map(lambda x: x.split(".session")[0], sessions))

    for session_name in sessions:
        try:
            cli = NotPx(SESSIONS_DIR + session_name)

            previous_balance = None  # Track previous balance

            async def run_painters():
                await painters(cli, session_name)

            async def run_mine_claimer():
                nonlocal previous_balance
                while True:
                    # Simulating balance check (replace with actual logic)
                    current_balance = cli.get_balance(session_name)  # Assuming this function exists
                    if previous_balance is not None:
                        points_earned = current_balance - previous_balance
                        if points_earned > 0:
                            # Use the print_auto_remove function for the red message
                            threading.Thread(target=print_auto_remove, args=(f"{Colors.GREEN}[+] {session_name}: {points_earned} Pixel painted successfully.{Colors.END}", 15)).start()
                            if points_earned >= 10:
                                smooth_print(f"{Colors.CYAN}BONUS! {points_earned}+ points earned!{Colors.END}")
                    previous_balance = current_balance
                    await asyncio.sleep(3)  # Assuming the script checks every 3 seconds

            # Create new event loops for both threads
            painter_loop = asyncio.new_event_loop()
            claimer_loop = asyncio.new_event_loop()

            threading.Thread(target=run_async_in_thread, args=(painter_loop, run_painters())).start()
            threading.Thread(target=run_async_in_thread, args=(claimer_loop, run_mine_claimer())).start()

        except Exception as e:
            smooth_print(f"{Colors.RED}[!] Error loading session '{session_name}', error: {e}{Colors.END}")

# Main process function to handle menu interaction
def process():
    clear_console()  # Clear console output when the script runs
    smooth_print(r"""{}
███████  █████  ██    ██  █████  ███    ██ 
██      ██   ██ ██    ██ ██   ██ ████   ██ 
███████ ███████ ██    ██ ███████ ██ ██  ██ 
     ██ ██   ██  ██  ██  ██   ██ ██  ██ ██ 
███████ ██   ██   ████   ██   ██ ██   ████ 
                                                
            NotPx Auto Paint & Claim by @sgr - v1.0 {}""".format(Colors.BLUE, Colors.END))
    
    while True:
        print("\n" + Colors.BLUE + "Main Menu:" + Colors.END)
        print("1. Add Account Session")
        print("2. Start Mine + Claim")
        print("3. Add API ID and Hash")
        print("4. Reset API Credentials")
        print("5. Reset Session")
        print("6. Show Available Sessions")
        print("7. Exit")
        
        option = input(Colors.YELLOW + "Enter your choice: " + Colors.END)

        if option == "1":
            name = input("\nEnter Session name: ")
            if not os.path.exists(SESSIONS_DIR):
                os.mkdir(SESSIONS_DIR)
            if not any(name in i for i in os.listdir(SESSIONS_DIR)):
                api_id, api_hash = load_api_credentials()
                if api_id and api_hash:
                    client = TelegramClient(SESSIONS_DIR + name, api_id, api_hash).start()
                    client.disconnect()
                    smooth_print(f"{Colors.GREEN}[+] Session '{name}' saved successfully.{Colors.END}")
                else:
                    smooth_print(f"{Colors.RED}[!] API credentials not found. Please add them first.{Colors.END}")
            else:
                smooth_print(f"{Colors.RED}[x] Session '{name}' already exists.{Colors.END}")
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
            smooth_print("Exiting...")
            break
        else:
            smooth_print(f"{Colors.RED}[!] Invalid option. Please try again.{Colors.END}")

if __name__ == "__main__":
    if not os.path.exists(SESSIONS_DIR):
        os.mkdir(SESSIONS_DIR)
    process()
