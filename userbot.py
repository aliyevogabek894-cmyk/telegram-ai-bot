import os
import sys
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAudio
from ai_service import generate_ai_response
from voice_service import text_to_voice_file

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

# 75 ta belgidan oshsa — 100% OVOZLI XABAR
VOICE_THRESHOLD_CHARS = 75

@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    """Shaxsiy chatlardan kelgan har qanday xabarga ZUDLIK BILAN javob qaytarish"""
    try:
        if not event.is_private or event.out:
            return

        sender = await event.get_sender()
        if not sender or getattr(sender, 'bot', False):
            return

        sender_id = event.sender_id
        sender_name = getattr(sender, 'first_name', '') or 'Foydalanuvchi'
        user_text = event.raw_text or ""

        # Ovozli xabar kelsa
        if event.voice or event.audio:
            print(f"🎙️ [VOICE KELDI] {sender_name}")
            await event.reply("Hozir ovozli xabarni eshita olmayotgan edim, nima gapligini yozib yuborolmaysizmi?")
            return

        # Rasm yoki video kelsa
        if event.photo or event.video:
            print(f"🖼️ [MEDIA KELDI] {sender_name}")
            if user_text:
                ai_reply = await generate_ai_response(sender_id, f"[Rasm/Video yubordi]: {user_text}")
            else:
                ai_reply = "Ko'rdim, qabul qildim. Hozir sal bo'shashim bilan qarab chiqaman."
            await event.reply(ai_reply)
            return

        if not user_text.strip():
            return

        print(f"\n⚡ [XABAR KELDI] {sender_name}: {user_text}")

        # AI dan javob olish
        ai_reply = await generate_ai_response(sender_id, user_text)
        print(f"🤖 [AI MATNI] ({len(ai_reply)} ta belgi): {ai_reply}")

        # 75 belgidan oshsa -> OVOZLI XABAR jo'natish
        if len(ai_reply) >= VOICE_THRESHOLD_CHARS:
            print(f"🎙️ [OVOZ TAYYORLANMOQDA...] ({len(ai_reply)} belgi >= {VOICE_THRESHOLD_CHARS})")
            
            # Chatda "recording voice..." statusini yoqamiz
            async with client.action(event.chat_id, 'record-voice'):
                voice_filename = f"v_{sender_id}_{int(time.time())}.ogg"
                voice_file = await text_to_voice_file(ai_reply, voice_filename)

                if voice_file and os.path.exists(voice_file) and os.path.getsize(voice_file) > 0:
                    try:
                        # Telegram Voice Note sifatiga kafolatli yuborish
                        await client.send_file(
                            event.chat_id,
                            voice_file,
                            voice_note=True,
                            reply_to=event.id,
                            attributes=[DocumentAttributeAudio(voice=True, title="Voice message", performer="")]
                        )
                        print(f"🚀 [OVOZLI XABAR 100% YUBORILDI!] -> {sender_name}\n")
                        try:
                            os.remove(voice_file)
                        except Exception:
                            pass
                        return
                    except Exception as send_err:
                        print(f"❌ Telegram send_file xatosi: {send_err}")
                else:
                    print("⚠️ Ovoz fayli yaratilmadi.")

        # 75 belgidan kam bo'lsa -> Oddiy matn
        await event.reply(ai_reply)
        print(f"🚀 [MATN YUBORILDI] -> {sender_name}: {ai_reply}\n")

    except Exception as e:
        print(f"❌ Xatolik yuz berdi: {e}")

async def main():
    print("==================================================")
    print("🌐 24/7 BULUT SERVERIDA KAFOLATLANGAN OVOZLI BOT...")
    print(f"📏 Ovoz chegarasi: {VOICE_THRESHOLD_CHARS} ta belgi")
    print("==================================================")

    threading.Thread(target=run_http_server, daemon=True).start()

    await client.connect()
    me = await client.get_me()
    print(f"✅ BOT ISHLAMOQDA!")
    print(f"👤 Egasi: {me.first_name} (@{me.username or 'usernamesiz'})")
    print("==================================================")

    await client.run_until_disconnected()

if __name__ == "__main__":
    loop.run_until_complete(main())
