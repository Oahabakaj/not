import os
import threading
import asyncio
import time
import sys
import nest_asyncio
from bot.painter import painters  # Assuming bot.painter has the 'painters' function
from bot.mineclaimer import mine_claimer  # Assuming bot.mineclaimer has the 'mine_claimer' function
from bot.utils import Colors  # Assuming bot.utils has the 'Colors' class for colored output
from telethon.sync import TelegramClient  # Telethon client for Telegram interactions

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
                    # Fetch the real balance
                    current_balance = await cli.get_balance()  # Now using the async method
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
        print("3. Show Account Balance")
        print("4. Add API ID and Hash")
        print("5. Reset API Credentials")
        print("6. Reset Session")
        print("7. Show Available Sessions")
        print("8. Exit")
        
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
            show_balance()
        elif option == "4":
            add_api_credentials()
        elif option == "5":
            reset_api_credentials()
        elif option == "6":
            reset_session()
        elif option == "7":
            show_sessions()
        elif option == "8":
            smooth_print("Exiting...")
            break
        else:
            smooth_print(f"{Colors.RED}[!] Invalid option. Please try again.{Colors.END}")

# NotPx class with the real get_balance method
class NotPx:
    def __init__(self, session_file):
        self.session_file = session_file
        self.account_status = "active"  # Default status; adjust based on your application's logic
        self.balance = 0  # Initialize balance

    async def get_balance(self):
        await asyncio.sleep(1)  # Simulate network delay
        # Here you should implement the actual balance fetching logic
        self.balance = 784.3090041666334  # Replace with actual logic to fetch balance
        return self.balance

    def accountStatus(self):
        return self.account_status  # Returns the current status of the account

def show_balance():
    session_name = input("Enter the session name to check balance: ")
    session_path = os.path.join(SESSIONS_DIR, f"{session_name}.session")
    if os.path.exists(session_path):
        cli = NotPx(session_path)
        balance = asyncio.run(cli.get_balance())
        smooth_print(f"{Colors.BLUE}Account Balance for '{session_name}': {balance} {Colors.END}")
    else:
        smooth_print(f"{Colors.RED}[!] Session '{session_name}' does not exist.{Colors.END}")

def show_sessions():
    if not os.path.exists(SESSIONS_DIR) or not os.listdir(SESSIONS_DIR):
        smooth_print(f"{Colors.RED}[!] No sessions available.{Colors.END}")
    else:
        smooth_print(f"{Colors.BLUE}Available sessions:{Colors.END}")
        for session in os.listdir(SESSIONS_DIR):
            if session.endswith('.session'):
                smooth_print(f"- {session[:-8]}")  # Remove .session for display

# Example functions for adding API credentials and resetting sessions (stub functions)
def add_api_credentials():
    # Functionality for adding API credentials goes here
    smooth_print(f"{Colors.YELLOW}[!] Add API credentials functionality not implemented.{Colors.END}")

def reset_api_credentials():
    # Functionality for resetting API credentials goes here
    smooth_print(f"{Colors.YELLOW}[!] Reset API credentials functionality not implemented.{Colors.END}")

def reset_session():
    # Functionality for resetting sessions goes here
    smooth_print(f"{Colors.YELLOW}[!] Reset session functionality not implemented.{Colors.END}")

if __name__ == "__main__":
    if not os.path.exists(SESSIONS_DIR):
        os.mkdir(SESSIONS_DIR)
    process()  # Start the main menu process
