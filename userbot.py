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

sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()

async def health_check(request):
    return web.Response(text="Bot 24/7 ishlamoqda!")

client = TelegramClient("bot_cloud_session", API_ID, API_HASH)

VOICE_THRESHOLD_CHARS = 20

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
            print(f"🎙️ [VOICE KELDI] {sender_name}", flush=True)
            await event.reply("Hozir ovozli xabarni eshita olmayotgan edim, nima gapligini yozib yuborolmaysizmi?")
            return

        if event.photo or event.video:
            print(f"🖼️ [MEDIA KELDI] {sender_name}", flush=True)
            if user_text:
                ai_reply = await generate_ai_response(sender_id, f"[Rasm/Video yubordi]: {user_text}")
            else:
                ai_reply = "Ko'rdim, qabul qildim. Hozir sal bo'shashim bilan qarab chiqaman."
            await event.reply(ai_reply)
            return

        if not user_text.strip():
            return

        print(f"\n⚡ [XABAR KELDI] {sender_name}: {user_text}", flush=True)

        # AI dan javob olish
        ai_reply = await generate_ai_response(sender_id, user_text)
        print(f"🤖 [AI JAVOBI]: {ai_reply}", flush=True)

        # 20 belgidan oshsa -> OVOZLI XABAR jo'natish
        if len(ai_reply) >= VOICE_THRESHOLD_CHARS:
            print(f"🎙️ [GOOGLE TTS OVOZ YARATILMOQDA...] ({len(ai_reply)} belgi)", flush=True)
            voice_filename = f"v_{sender_id}_{int(time.time())}.mp3"
            try:
                voice_file = await text_to_voice_file(ai_reply, voice_filename)
                if voice_file and os.path.exists(voice_file) and os.path.getsize(voice_file) > 0:
                    # Telegram voice shaklida yuborish
                    await client.send_file(
                        event.chat_id,
                        voice_file,
                        voice_note=True,
                        reply_to=event.id
                    )
                    print(f"🚀 [OVOZLI XABAR 100% YUBORILDI!] -> {sender_name}\n", flush=True)
                    try:
                        os.remove(voice_file)
                    except Exception:
                        pass
                    return
                else:
                    print("⚠️ Audio fayl topilmadi, matn yuboriladi.", flush=True)
            except Exception as ve:
                print(f"❌ Telegram send_file xatosi: {ve}", flush=True)

        # Matn qilib yuborish
        await event.reply(ai_reply)
        print(f"🚀 [MATN YUBORILDI] -> {sender_name}: {ai_reply}\n", flush=True)

    except Exception as e:
        print(f"❌ Handler xatosi: {e}", flush=True)

async def main():
    print("==================================================", flush=True)
    print("🚀 PURE GTTS TELEGRAM USERBOT ISHGA TUSHMOQDA...", flush=True)
    print("==================================================", flush=True)

    await client.connect()
    if not await client.is_user_authorized():
        print("❌ XATOLIK: bot_cloud_session avtorizatsiyadan o'tmagan!", flush=True)
        return

    me = await client.get_me()
    print(f"✅ TELEGRAM AKKAUNTGA ULIK: {me.first_name} (@{me.username or 'usernamesiz'})", flush=True)
    print(f"📏 Ovoz chegarasi: {VOICE_THRESHOLD_CHARS} ta belgi", flush=True)
    print("==================================================", flush=True)

    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 HTTP Server faol (port {port})", flush=True)

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
