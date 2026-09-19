import os
import sys
import asyncio
from aiohttp import web
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from telethon import TelegramClient, events, connection
from telethon.tl import types
from telethon.tl.types import DocumentAttributeAudio
from telethon.errors import (
    FloodWaitError, AuthKeyDuplicatedError,
    SessionPasswordNeededError, RPCError
)
from ai_service import generate_ai_response
from voice_service import text_to_voice_file, get_voice_waveform_and_duration

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(line_buffering=True, encoding='utf-8', errors='replace')
    except Exception:
        pass

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()

# Har qanday javob — OVOZLI XABAR bo'lib ketsin
VOICE_THRESHOLD_CHARS = 1

# Javob bermasangiz kutish vaqti (25 soniya)
AUTO_REPLY_DELAY = 25

async def health_check(request):
    return web.Response(text="Bot 24/7 ishlamoqda!")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

client = TelegramClient(
    "bot_cloud_session",
    API_ID,
    API_HASH,
    connection=connection.ConnectionTcpIntermediate,
    timeout=30,
    retry_delay=5,
    connection_retries=999,
    auto_reconnect=True,
    loop=loop
)

@client.on(events.NewMessage(outgoing=True))
async def handle_outgoing(event):
    """Egasi Telegramda xabar yozsa, faollik vaqtini yangilaymiz"""
    pass  # faqat ro'yxatga olish uchun mavjud

async def send_ai_reply(chat_id: int, sender_id: int, sender_name: str, user_text: str, incoming_msg_id: int):
    """
    25 soniya javob berilmasa — AI ovozli xabar yuboradi.
    Siz o'zingiz javob yozsangiz — bot bekor qilinadi.
    Online/offline farq qilmaydi.
    """
    try:
        start_time = time.time()
        max_wait_seconds = 1800  # Eng ko'pi 30 daqiqa

        print(f"[NAVBAT] {sender_name}: '{user_text[:40]}' — 25 soniya kutilmoqda...", flush=True)

        while True:
            await asyncio.sleep(3)

            # 1. O'zingiz javob yozdingizmi?
            try:
                messages = await client.get_messages(chat_id, limit=5)
                for msg in messages:
                    if msg.out and msg.id > incoming_msg_id:
                        print(f"[BEKOR] {sender_name}: O'zingiz javob yozdingiz.", flush=True)
                        return
            except FloodWaitError as fw:
                print(f"[FLOOD] get_messages: {fw.seconds}s kutilmoqda...", flush=True)
                await asyncio.sleep(fw.seconds)
                continue
            except Exception as e:
                print(f"[WARN] get_messages: {e}", flush=True)

            elapsed = time.time() - start_time

            if elapsed > max_wait_seconds:
                print(f"[TIMEOUT] {sender_name}: 30 daqiqa o'tdi, bekor qilindi.", flush=True)
                return

            # 2. 25 soniya o'tdi — yuborish vaqti!
            if elapsed >= AUTO_REPLY_DELAY:
                print(f"[25 SONIYA] {sender_name} uchun AI ovozli javob tayyorlanmoqda...", flush=True)
                break

        # ── AI javob olish ──────────────────────────────────────
        try:
            ai_reply = await generate_ai_response(sender_id, user_text)
        except Exception as e:
            print(f"[AI ERROR] {e}", flush=True)
            ai_reply = "Hozir band edim, birozdan keyin yozaman."

        print(f"[AI] {ai_reply}", flush=True)

        # ── Ovozli xabar yuborish ───────────────────────────────
        if len(ai_reply) >= VOICE_THRESHOLD_CHARS:
            voice_filename = f"v_{sender_id}_{int(time.time())}.ogg"
            try:
                async with client.action(chat_id, 'record-audio'):
                    voice_file = await text_to_voice_file(ai_reply, voice_filename)

                if voice_file and os.path.exists(voice_file) and os.path.getsize(voice_file) > 0:
                    try:
                        voice_attr = get_voice_waveform_and_duration(voice_file, ai_reply)
                        await client.send_file(
                            chat_id, voice_file,
                            voice_note=True,
                            attributes=[voice_attr],
                            reply_to=incoming_msg_id
                        )
                        print(f"[OVOZ YUBORILDI] -> {sender_name}", flush=True)
                    except FloodWaitError as fw:
                        print(f"[FLOOD] send_file: {fw.seconds}s kutilmoqda...", flush=True)
                        await asyncio.sleep(fw.seconds)
                        await client.send_file(
                            chat_id, voice_file,
                            voice_note=True,
                            reply_to=incoming_msg_id
                        )
                    except Exception as e:
                        print(f"[WARN] Waveform bilan xato ({e}), oddiy yuborilmoqda...", flush=True)
                        await client.send_file(
                            chat_id, voice_file,
                            voice_note=True,
                            reply_to=incoming_msg_id
                        )
                        print(f"[OVOZ YUBORILDI - oddiy] -> {sender_name}", flush=True)
                    finally:
                        try:
                            os.remove(voice_file)
                        except Exception:
                            pass
                    return
                else:
                    print("[WARN] Ovoz fayli yaratilmadi, matn yuboriladi.", flush=True)
            except Exception as ve:
                print(f"[VOICE ERROR] {ve}", flush=True)

        # ── Matn yuborish (zaxira) ──────────────────────────────
        try:
            await client.send_message(chat_id, ai_reply, reply_to=incoming_msg_id)
            print(f"[MATN YUBORILDI] -> {sender_name}", flush=True)
        except FloodWaitError as fw:
            print(f"[FLOOD] send_message: {fw.seconds}s kutilmoqda...", flush=True)
            await asyncio.sleep(fw.seconds)
            await client.send_message(chat_id, ai_reply, reply_to=incoming_msg_id)
        except Exception as e:
            print(f"[ERROR] send_message: {e}", flush=True)

    except asyncio.CancelledError:
        pass
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

        print(f"\n[YANGI XABAR] {sender_name}: {user_text}", flush=True)

        asyncio.create_task(send_ai_reply(
            event.chat_id, sender_id, sender_name,
            user_text, event.id
        ))

    except Exception as e:
        print(f"[ERROR] handle_incoming: {e}", flush=True)


async def start_http_server():
    """Health check HTTP server"""
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[OK] HTTP Server faol (port {port})", flush=True)


async def run_bot():
    """Botni ishga tushirish — uzilsa avtomatik qayta ulanadi"""
    while True:
        try:
            print("==================================================", flush=True)
            print("TELEGRAM USERBOT — 25 SONIYADA OVOZLI JAVOB", flush=True)
            print("==================================================", flush=True)

            await client.connect()

            if not await client.is_user_authorized():
                print("[ERROR] Session avtorizatsiyadan o'tmagan! Qayta login qiling.", flush=True)
                return

            me = await client.get_me()
            print(f"[OK] Ulandi: {me.first_name} (@{me.username or 'usernamesiz'})", flush=True)
            print(f"[OK] Kutish vaqti: {AUTO_REPLY_DELAY} soniya", flush=True)
            print("==================================================", flush=True)

            await client.run_until_disconnected()

        except AuthKeyDuplicatedError:
            print("[XATO] Session boshqa joyda ishlamoqda! 30 soniyadan keyin qayta uriniladi...", flush=True)
            await asyncio.sleep(30)

        except FloodWaitError as fw:
            print(f"[FLOOD] Telegram: {fw.seconds}s kutilmoqda...", flush=True)
            await asyncio.sleep(fw.seconds)

        except (ConnectionError, OSError) as e:
            print(f"[UZILDI] Internet uzildi: {e} — 10 soniyadan keyin qayta ulaniladi...", flush=True)
            await asyncio.sleep(10)

        except Exception as e:
            print(f"[KRITIK XATO] {e} — 15 soniyadan keyin qayta uriniladi...", flush=True)
            await asyncio.sleep(15)

        finally:
            try:
                await client.disconnect()
            except Exception:
                pass

        print("[QAYTA ULANISH] Yangi ulanish boshlanmoqda...", flush=True)


async def keep_alive():
    """Har 10 daqiqada Telegramga ping yuborib, bot uxlamasligini ta'minlaydi"""
    await asyncio.sleep(60)  # Boshlanganda 1 daqiqa kutamiz
    while True:
        try:
            if client.is_connected():
                await client.get_me()
                print("[PING] Bot tirik, uxlamayapti ✓", flush=True)
        except Exception as e:
            print(f"[PING WARN] {e}", flush=True)
        await asyncio.sleep(600)  # Har 10 daqiqada


async def main():
    await asyncio.gather(
        start_http_server(),
        run_bot(),
        keep_alive()
    )

if __name__ == "__main__":
    loop.run_until_complete(main())
