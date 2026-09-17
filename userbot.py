import os
import sys
import asyncio
from aiohttp import web
import time
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAudio
from ai_service import generate_ai_response
from voice_service import text_to_voice_file

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(line_buffering=True, encoding='utf-8', errors='replace')
    except Exception:
        pass

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()

async def health_check(request):
    return web.Response(text="Bot 24/7 ishlamoqda!")

client = TelegramClient("bot_cloud_session", API_ID, API_HASH)

# 20 ta belgidan oshsa — OVOZLI XABAR
VOICE_THRESHOLD_CHARS = 20

# Siz o'zingiz javob bermasangiz, necha soniyadan keyin bot javob bersin (1 daqiqa)
AUTO_REPLY_DELAY = 60

async def send_ai_reply(chat_id: int, sender_id: int, sender_name: str, user_text: str, incoming_msg_id: int):
    """1 daqiqa kutib, agar siz javob bermagan bo'lsangiz — bot yuboradi"""
    try:
        # 1 daqiqa kutish
        await asyncio.sleep(AUTO_REPLY_DELAY)

        # 1 daqiqa ichida siz (akkaunt egasi) javob yozganmisiz?
        messages = await client.get_messages(chat_id, limit=15)
        for msg in messages:
            # event.id dan keyin chiqqan chiquvchi (out=True) xabar bo'lsa — siz yozdingiz
            if msg.out and msg.id > incoming_msg_id:
                print(f"[SKIP] {sender_name}: Siz o'zingiz javob berdingiz, bot jim.", flush=True)
                return

        print(f"\n[XABAR KELDI] {sender_name}: {user_text}", flush=True)

        # AI javob olish
        ai_reply = await generate_ai_response(sender_id, user_text)
        print(f"[AI JAVOBI]: {ai_reply}", flush=True)

        # 20 belgidan oshsa -> OVOZLI XABAR
        if len(ai_reply) >= VOICE_THRESHOLD_CHARS:
            print(f"[OVOZ YARATILMOQDA] ({len(ai_reply)} belgi)...", flush=True)
            voice_filename = f"v_{sender_id}_{int(time.time())}.ogg"
            try:
                voice_file = await text_to_voice_file(ai_reply, voice_filename)
                if voice_file and os.path.exists(voice_file) and os.path.getsize(voice_file) > 0:
                    await client.send_file(
                        chat_id,
                        voice_file,
                        voice_note=True,
                        reply_to=incoming_msg_id
                    )
                    print(f"[OVOZLI XABAR YUBORILDI] -> {sender_name}", flush=True)
                    try:
                        os.remove(voice_file)
                    except Exception:
                        pass
                    return
                else:
                    print("[WARN] Ovoz fayli yaratilmadi, matn yuboriladi.", flush=True)
            except Exception as ve:
                print(f"[ERROR] send_file: {ve}", flush=True)

        # Qisqa bo'lsa yoki ovoz yaratilmasa — matn
        await client.send_message(chat_id, ai_reply, reply_to=incoming_msg_id)
        print(f"[MATN YUBORILDI] -> {sender_name}: {ai_reply}", flush=True)

    except Exception as e:
        print(f"[ERROR] send_ai_reply: {e}", flush=True)


@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    try:
        if not event.is_private or event.out:
            return

        sender = await event.get_sender()
        if not sender or getattr(sender, 'bot', False):
            return

        sender_id = event.sender_id
        sender_name = getattr(sender, 'first_name', '') or 'Foydalanuvchi'
        user_text = event.raw_text or ""

        if event.voice or event.audio:
            print(f"[VOICE KELDI] {sender_name}", flush=True)
            # Ovozli xabarga ham 1 daqiqa kutib javob ber
            asyncio.create_task(send_ai_reply(
                event.chat_id, sender_id, sender_name,
                "[Ovozli xabar yubordi]", event.id
            ))
            return

        if event.photo or event.video:
            print(f"[MEDIA KELDI] {sender_name}", flush=True)
            caption = user_text if user_text else "[Rasm yoki video yubordi]"
            asyncio.create_task(send_ai_reply(
                event.chat_id, sender_id, sender_name,
                caption, event.id
            ))
            return

        if not user_text.strip():
            return

        print(f"[XABAR QABUL QILINDI] {sender_name}: {user_text} — 1 daqiqa kutilmoqda...", flush=True)

        # 1 daqiqa kutib, agar siz javob bermagan bo'lsangiz — bot yuboradi
        asyncio.create_task(send_ai_reply(
            event.chat_id, sender_id, sender_name,
            user_text, event.id
        ))

    except Exception as e:
        print(f"[ERROR] handle_incoming: {e}", flush=True)


async def main():
    print("==================================================", flush=True)
    print("TELEGRAM USERBOT — 1 DAQIQA KUTIB JAVOB BERUVCHI", flush=True)
    print("==================================================", flush=True)

    await client.connect()
    if not await client.is_user_authorized():
        print("[ERROR] bot_cloud_session avtorizatsiyadan otmagan!", flush=True)
        return

    me = await client.get_me()
    print(f"[OK] Ulandi: {me.first_name} (@{me.username or 'usernamesiz'})", flush=True)
    print(f"[OK] Ovoz chegarasi: {VOICE_THRESHOLD_CHARS} belgi", flush=True)
    print(f"[OK] Kutish vaqti: {AUTO_REPLY_DELAY} soniya (1 daqiqa)", flush=True)
    print("==================================================", flush=True)

    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[OK] HTTP Server faol (port {port})", flush=True)

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
