import os
import sys
import shutil
import asyncio

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(line_buffering=True, encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(line_buffering=True, encoding='utf-8', errors='replace')
    except Exception:
        pass

from dotenv import load_dotenv
from telethon import TelegramClient, connection
from telethon.errors import SessionPasswordNeededError

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()
DEFAULT_PHONE = "+998950892225"

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def get_client():
    c = TelegramClient(
        "bot_cloud_session",
        API_ID,
        API_HASH,
        timeout=20,
        retry_delay=1,
        auto_reconnect=True,
        loop=loop
    )
    c.session.set_dc(2, "149.154.167.51", 80)
    return c

async def login():
    client = get_client()
    await client.connect()
    
    if not await client.is_user_authorized():
        print("==================================================")
        print("📲 TELEGRAM AKKAUNTGA ULASH (LOGIN)")
        print("==================================================")
        phone = DEFAULT_PHONE
        print(f"\n📲 {phone} raqamingizga Telegram orqali tasdiqlash kodi yuborilmoqda...")
        sent_code = await client.send_code_request(phone)
        print("✅ Tasdiqlash kodi Telegram ilovangizga (yoki SMS) yuborildi!")
        
        code = input("\n👉 Telegram ilovangizga kelgan 5 xonali KODNI kiriting: ").strip().replace(" ", "").replace("-", "")
        
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=sent_code.phone_code_hash)
        except SessionPasswordNeededError:
            print("\n🔒 Akkauntingizda 2-bosqichli himoya paroli (Cloud Password) yoqilgan.")
            pwd = input("👉 2-bosqichli parolingizni kiriting: ").strip()
            await client.sign_in(password=pwd)
        except Exception as e:
            if "password" in str(e).lower():
                pwd = input("👉 2-bosqichli parolingizni kiriting: ").strip()
                await client.sign_in(password=pwd)
            else:
                raise e

    me = await client.get_me()
    print("\n" + "=" * 50)
    print("🎉 TABRIKLAYMIZ! AKKAUNT MUVAFFAQIYATLI ULANDI!")
    print(f"👤 Ism: {me.first_name}")
    if me.last_name:
        print(f"👤 Familiya: {me.last_name}")
    print(f"🔗 Username: @{me.username or 'usernamesiz'}")
    print(f"📞 Telefon: {me.phone}")
    print("=" * 50)
    
    await client.disconnect()
    
    # my_userbot_session.session faylini ham yangilab qo'yamiz
    try:
        if os.path.exists("bot_cloud_session.session"):
            shutil.copyfile("bot_cloud_session.session", "my_userbot_session.session")
    except Exception:
        pass

    print("\n✅ Sessiya fayllari saqlandi! Endi botni ishga tushirishingiz mumkin.\n")

if __name__ == "__main__":
    try:
        loop.run_until_complete(login())
    except KeyboardInterrupt:
        print("\n❌ Jarayon bekor qilindi.")
    except Exception as e:
        print(f"\n❌ Xatolik yuz berdi: {e}")

