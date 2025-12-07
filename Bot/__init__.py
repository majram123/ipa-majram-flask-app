from pyrogram import Client
from pyrogram.errors import FloodWait
import pyromod
import os
import asyncio

api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
api_hash = os.getenv("TELEGRAM_API_HASH", "")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")

app = Client(
    name="MediaDownloader", 
    api_id=api_id, 
    api_hash=api_hash, 
    bot_token=bot_token,
    in_memory=False, 
    plugins=dict(root="Bot/handlers"),
    workers=20
)
