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
    retry_delay=2,
    connection_retries=10,
    auto_reconnect=True,
    loop=loop
)

# 20 ta belgidan oshsa — OVOZLI XABAR
VOICE_THRESHOLD_CHARS = 20

# Chiqib ketganingizdan keyin yoki javob bermasangiz kutish vaqti (60 soniya = 1 daqiqa)
AUTO_REPLY_DELAY = 60

# Egasi (Og'abek) oxirgi marta qachon xabar yozgan vaqti
last_owner_activity_time = 0.0

@client.on(events.NewMessage(outgoing=True))
async def handle_outgoing(event):
    """Egasi Telegramda xabar yozsa, faollik vaqtini yangilaymiz"""
    global last_owner_activity_time
    last_owner_activity_time = time.time()

async def is_owner_online_or_recently_active() -> bool:
    """
    Egasi hozir onlinemi yoki chiqib ketganiga hali 1 minut to'lmadimi:
    - Agar online bo'lsa -> True
    - Chiqib ketganiga 60 soniyadan kam bo'lsa -> True
    - Aks holda (1 minutdan ko'p offline bo'lsa) -> False
    """
    now_ts = time.time()
    # 1. Yaqinda (60 soniya ichida) biror joyga xabar yuborgan bo'lsa
    if now_ts - last_owner_activity_time < AUTO_REPLY_DELAY:
        return True

    # 2. Telegram statusini tekshirish
    try:
        me = await client.get_entity('me')
        if hasattr(me, 'status') and me.status:
            # Agar ayni paytda online bo'lsa
            if isinstance(me.status, types.UserStatusOnline):
                return True
            # Agar offline bo'lsa, chiqib ketganiga 60 soniya bo'ldimi?
            if isinstance(me.status, types.UserStatusOffline) and hasattr(me.status, 'was_online') and me.status.was_online:
                now_utc = datetime.now(timezone.utc)
                diff = (now_utc - me.status.was_online).total_seconds()
                if diff < AUTO_REPLY_DELAY:
                    return True
    except Exception as e:
        print(f"[STATUS CHECK WARN] {e}", flush=True)

    return False

async def send_ai_reply(chat_id: int, sender_id: int, sender_name: str, user_text: str, incoming_msg_id: int):
    """
    Talab:
    - Online turganingizda ketmaydi.
    - Chiqib ketganingizga 1 minutdan oshgandan keyin va siz javob bermagan bo'lsangiz ketadi.
    - O'zingiz javob yozsangiz — bot bekor qilinadi.
    """
    try:
        start_time = time.time()
        max_wait_seconds = 1800  # Eng ko'pi 30 daqiqa kutish, keyin to'xtatish

        print(f"[NAVATGA OLINDI] {sender_name}: '{user_text[:30]}...' — Online/Javob holati nazoratda...", flush=True)

        while True:
            await asyncio.sleep(10)  # Har 10 soniyada holatni tekshiramiz

            # 1. Siz shu chatga o'zingiz javob yozdingizmi?
            messages = await client.get_messages(chat_id, limit=10)
            for msg in messages:
                if msg.out and msg.id > incoming_msg_id:
                    print(f"[BEKOR QILINDI] {sender_name}: Siz o'zingiz javob yozdingiz, bot to'xtatildi.", flush=True)
                    return

            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                print(f"[TIMEOUT] {sender_name}: 30 daqiqadan oshdi, vazifa bekor qilindi.", flush=True)
                return

            # Kamida 60 soniya kutish shart
            if elapsed < AUTO_REPLY_DELAY:
                continue

            # 2. Siz online turibsizmi yoki chiqib ketganingizga 1 minut to'lmadimi?
            is_active = await is_owner_online_or_recently_active()
            if is_active:
                # Egasi hali online yoki chiqib ketganiga 1 minut bo'lmagan -> kutishda davom etamiz
                continue

            # 3. Agar 1 minutdan oshgan bo'lsa va siz offline bo'lsangiz (va javob yozmagan bo'lsangiz):
            print(f"[CHIQIB KETILGAN: 1 MINUT O'TDI] {sender_name} uchun javob tayyorlanmoqda...", flush=True)
            break

        # AI dan javob olish
        ai_reply = await generate_ai_response(sender_id, user_text)
        print(f"[AI JAVOBI]: {ai_reply}", flush=True)

        # 20 belgidan oshsa -> OVOZLI XABAR
        if len(ai_reply) >= VOICE_THRESHOLD_CHARS:
            print(f"[OVOZ YARATILMOQDA] ({len(ai_reply)} belgi)...", flush=True)
            voice_filename = f"v_{sender_id}_{int(time.time())}.ogg"
            try:
                async with client.action(chat_id, 'record-audio'):
                    voice_file = await text_to_voice_file(ai_reply, voice_filename)
                    if voice_file and os.path.exists(voice_file) and os.path.getsize(voice_file) > 0:
                        voice_attr = get_voice_waveform_and_duration(voice_file, ai_reply)
                        # Faylni bytes sifatida o'qib, mime_type aniq ko'rsatamiz
                        import io
                        with open(voice_file, 'rb') as f:
                            voice_bytes = io.BytesIO(f.read())
                        # MP3 yoki OGG formatini aniqlash
                        ext = voice_file.rsplit('.', 1)[-1].lower() if '.' in voice_file else 'ogg'
                        mime = 'audio/mpeg' if ext == 'mp3' else 'audio/ogg'
                        voice_bytes.name = f"voice.{ext}"
                        await client.send_file(
                            chat_id,
                            voice_bytes,
                            voice_note=True,
                            attributes=[voice_attr],
                            mime_type=mime,
                            reply_to=incoming_msg_id
                        )
                        print(f"[OVOZLI XABAR YUBORILDI (WAVEFORM BILAN)] -> {sender_name}\n", flush=True)
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
        print(f"[MATN YUBORILDI] -> {sender_name}: {ai_reply}\n", flush=True)

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

        print(f"\n⚡ [YANGI XABAR] {sender_name}: {user_text}", flush=True)

        # Monitoring va javob berish vazifasini ishga tushirish
        asyncio.create_task(send_ai_reply(
            event.chat_id, sender_id, sender_name,
            user_text, event.id
        ))

    except Exception as e:
        print(f"[ERROR] handle_incoming: {e}", flush=True)


async def main():
    print("==================================================", flush=True)
    print("TELEGRAM USERBOT — FAQAT CHIQIB KETGANDA VA 1 MINUT O'TGANDA", flush=True)
    print("==================================================", flush=True)

    await client.connect()
    if not await client.is_user_authorized():
        print("[ERROR] bot_cloud_session avtorizatsiyadan otmagan!", flush=True)
        return

    me = await client.get_me()
    print(f"[OK] Ulandi: {me.first_name} (@{me.username or 'usernamesiz'})", flush=True)
    print(f"[OK] Ovoz chegarasi: {VOICE_THRESHOLD_CHARS} belgi", flush=True)
    print(f"[OK] Chiqib ketishni kutish: {AUTO_REPLY_DELAY} soniya (1 daqiqa)", flush=True)
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
    loop.run_until_complete(main())
