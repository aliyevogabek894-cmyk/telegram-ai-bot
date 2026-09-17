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

client = TelegramClient("my_userbot_session", API_ID, API_HASH, loop=loop)

async def login():
    await client.connect()
    
    if not await client.is_user_authorized():
        print(f"\n📲 {PHONE} raqamiga kod yuborilmoqda...")
        sent_code = await client.send_code_request(PHONE)
        print("✅ Kod Telegram ilovangizga (yoki SMS orqali) yuborildi!")
        
        code = input("\n👉 Telegramga kelgan kodni kiriting: ").strip()
        
        try:
            await client.sign_in(PHONE, code)
        except Exception as e:
            if "password" in str(e).lower() or "SessionPasswordNeededError" in str(type(e).__name__):
                pwd = input("🔒 Akkauntingizda 2-bosqichli parol (Cloud Password) bor. Parolni kiriting: ").strip()
                await client.sign_in(password=pwd)
            else:
                raise e

    me = await client.get_me()
    print(f"\n🎉 TABRIKLAYMIZ! Muvaffaqiyatli ulandi!")
    print(f"👤 Akkaunt: {me.first_name} (@{me.username or 'usernamesiz'})")
    print("Endi `python userbot.py` orqali AI javob botini bemalol ishlatishingiz mumkin.\n")
    await client.disconnect()

if __name__ == "__main__":
    loop.run_until_complete(login())
