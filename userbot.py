import os
import sys
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
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

# Bepul bulut server uchun HTTP Healthcheck
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot 24/7 ishlamoqda!")

    def log_message(self, format, *args):
        return

def run_http_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

client = TelegramClient("my_userbot_session", API_ID, API_HASH, loop=loop)

# Siz oxirgi marta har bir chatda qachon xabar yozganingizni eslab qolish
last_owner_activity = {}

@client.on(events.NewMessage(outgoing=True))
async def handle_outgoing(event):
    """Agar siz o'zingiz Telegramda birovga yozsangiz, bot bu chatda faollikni qayd qiladi va aralashmaydi"""
    if event.is_private:
        last_owner_activity[event.chat_id] = time.time()

@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    """Shaxsiy chatlardan kelgan yangi xabarlarga aqlli munosabat"""
    try:
        # Faqat shaxsiy yozishmalar
        if not event.is_private or event.out:
            return

        sender = await event.get_sender()
        if not sender or getattr(sender, 'bot', False):
            return

        chat_id = event.chat_id
        sender_id = event.sender_id
        sender_name = getattr(sender, 'first_name', '') or 'Foydalanuvchi'

        # 1-QOIDA: Agar siz o'zingiz oxirgi 3 daqiqa ichida bu odamga yozgan bo'lsangiz (siz online yozishyapsiz),
        # bot sizning suhbatingizga xalaqit bermaydi va jim turadi!
        now = time.time()
        if chat_id in last_owner_activity and (now - last_owner_activity[chat_id] < 180):
            print(f"🤫 Siz {sender_name} bilan o'zingiz yozishyapsiz, AI aralashmadi.")
            return

        # 2-QOIDA: Xabar turini aniqlash (Matn, Rasm, Video, Ovozli xabar)
        user_text = event.raw_text or ""

        # Agar ovozli xabar (Voice) bo'lsa
        if event.voice or event.audio:
            print(f"🎙️ [VOICE KELDI] {sender_name}")
            ai_reply = "Hozir ovozli xabarni eshita olmayotgan edim, nima gapligini yozib yuborolmaysizmi?"
            await event.reply(ai_reply)
            return

        # Agar rasm yoki video bo'lsa
        if event.photo or event.video:
            print(f"🖼️ [MEDIA KELDI] {sender_name}")
            if user_text:
                # Rasmni tagiga yozuv yozilgan bo'lsa, o'sha yozuvga AI javob beradi
                ai_reply = await generate_ai_response(sender_id, f"[Rasm/Video yubordi]: {user_text}")
            else:
                # Faqat rasm/videoning o'zi bo'lsa
                ai_reply = "Ko'rdim, qabul qildim. Hozir sal bo'shashim bilan qarab chiqaman."
            await event.reply(ai_reply)
            return

        # Agar oddiy matn bo'lmasa
        if not user_text.strip():
            return

        print(f"⚡ [XABAR] {sender_name}: {user_text}")

        # AI dan javob olish
        ai_reply = await generate_ai_response(sender_id, user_text)

        # Xabarga javob yuborish
        await event.reply(ai_reply)
        print(f"🚀 [JAVOB BERILDI] -> {sender_name}: {ai_reply}\n")

    except Exception as e:
        print(f"❌ Xatolik: {e}")

async def main():
    print("==================================================")
    print("🌐 24/7 BULUT SERVERIDA AQLI BOT ISHGA TUSHMOQDA...")
    print("==================================================")

    threading.Thread(target=run_http_server, daemon=True).start()

    await client.connect()
    me = await client.get_me()
    print(f"✅ BOT SMART REJIMDA ISHLAMOQDA!")
    print(f"👤 Egasi: {me.first_name} (@{me.username or 'usernamesiz'})")
    print("==================================================")

    await client.run_until_disconnected()

if __name__ == "__main__":
    loop.run_until_complete(main())
