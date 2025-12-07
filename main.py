from Bot import app
from pyrogram.errors import FloodWait
import os
import asyncio
import time

def main():
    print("Bot is starting...")
    try:
        app.run()
    except FloodWait as e:
        print(f"FloodWait error: Need to wait {e.value} seconds")
        print(f"Will retry after {e.value} seconds...")
        time.sleep(e.value)
        print("Retrying...")
        app.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
