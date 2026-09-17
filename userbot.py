import os
import sys
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
from ai_service import generate_ai_response

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

client = TelegramClient("my_userbot_session", API_ID, API_HASH, loop=loop)

@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    """Zudlik bilan (chaqmoqdek tez) javob qaytarish"""
    try:
        # Faqat shaxsiy yozishmalar va kiruvchi xabarlar
        if not event.is_private or event.out:
            return

        sender = await event.get_sender()
        if not sender or getattr(sender, 'bot', False):
            return

        user_text = event.raw_text
        if not user_text or not user_text.strip():
            return

        sender_id = event.sender_id
        sender_name = getattr(sender, 'first_name', '') or 'Foydalanuvchi'

        print(f"⚡ [XABAR] {sender_name}: {user_text}")

        # Parallel va tezkor generatsiya
        ai_reply = await generate_ai_response(sender_id, user_text)

        # To'g'ridan-to'g'ri darhol yuborish
        await event.reply(ai_reply)
        print(f"🚀 [JAVOB BERILDI] -> {sender_name}: {ai_reply}\n")

    except Exception as e:
        print(f"❌ Xatolik: {e}")

async def main():
    print("==================================================")
    print("⚡ TEZKOR SHAXSIY AI BOT ISHGA TUSHMOQDA...")
    print("==================================================")

    await client.connect()
    me = await client.get_me()
    print(f"✅ BOT ULTRA-TEZKOR REJIMDA ISHLAMOQDA!")
    print(f"👤 Egasi: {me.first_name} (@{me.username or 'usernamesiz'})")
    print("==================================================")

    await client.run_until_disconnected()

if __name__ == "__main__":
    loop.run_until_complete(main())
