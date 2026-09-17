import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()
PHONE = "+998950892225"

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Yangi toza nom: bot_cloud_session
client = TelegramClient("bot_cloud_session", API_ID, API_HASH, loop=loop)

async def login():
    await client.connect()
    if not await client.is_user_authorized():
        print(f"\n📲 {PHONE} raqamiga yangi kod yuborilmoqda...")
        await client.send_code_request(PHONE)
        print("✅ Kod Telegram ilovangizga yuborildi!")
        code = input("\n👉 Yangi kelgan kodni kiriting: ").strip()
        try:
            await client.sign_in(PHONE, code)
        except Exception as e:
            if "password" in str(e).lower():
                pwd = input("🔒 2-bosqichli parol: ").strip()
                await client.sign_in(password=pwd)
            else:
                raise e

    me = await client.get_me()
    print(f"\n🎉 YANGI TOZA SESSIYA YARATILDI: {me.first_name} (@{me.username})")
    await client.disconnect()

if __name__ == "__main__":
    loop.run_until_complete(login())
