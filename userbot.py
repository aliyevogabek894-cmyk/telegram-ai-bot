import os
import sys
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from dotenv import load_dotenv
from telethon import TelegramClient, events
from ai_service import generate_ai_response

# Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()

# Bepul bulut server (Render Free Web Service) uchun kichik Healthcheck serveri
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

@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    try:
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

        ai_reply = await generate_ai_response(sender_id, user_text)

        await event.reply(ai_reply)
        print(f"🚀 [JAVOB BERILDI] -> {sender_name}: {ai_reply}\n")

    except Exception as e:
        print(f"❌ Xatolik: {e}")

async def main():
    print("==================================================")
    print("🌐 24/7 BULUT SERVERIDA BOT ISHGA TUSHMOQDA...")
    print("==================================================")

    # HTTP serverni alohida oqimda ishga tushiramiz
    threading.Thread(target=run_http_server, daemon=True).start()

    await client.connect()
    me = await client.get_me()
    print(f"✅ BOT 24/7 SERVERDA ISHLAMOQDA!")
    print(f"👤 Egasi: {me.first_name} (@{me.username or 'usernamesiz'})")
    print("==================================================")

    await client.run_until_disconnected()

if __name__ == "__main__":
    loop.run_until_complete(main())
