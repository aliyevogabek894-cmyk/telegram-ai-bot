import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()

async def check():
    client = TelegramClient("my_userbot_session", API_ID, API_HASH)
    await client.connect()
    is_auth = await client.is_user_authorized()
    if is_auth:
        me = await client.get_me()
        print(f"STATUS_OK: {me.first_name} (@{me.username})")
    else:
        print("STATUS_NOT_LOGGED_IN")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check())
