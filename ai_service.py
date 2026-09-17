import time
import os
import sys
from typing import Dict
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OWNER_NAME = "Og'abek"

# 500 xatosi bermasligi uchun barqaror modellar navbati
PRIMARY_MODEL = "gemma-4-26b-a4b-it"

user_conversations: Dict[int, Dict] = {}
SESSION_TIMEOUT_SECONDS = 3600

def get_ai_client():
    key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()
    return genai.Client(api_key=key)

async def generate_ai_response(user_id: int, user_message: str) -> str:
    clean_message = user_message.strip()

    if user_id not in user_conversations:
        user_conversations[user_id] = {
            "last_active": time.time(),
            "history": []
        }
    
    user_data = user_conversations[user_id]
    user_data["last_active"] = time.time()
    
    dialogue = ""
    for msg in user_data["history"][-4:]:
        speaker = "Suhbatdosh" if msg["role"] == "user" else OWNER_NAME
        dialogue += f"{speaker}: {msg['text']}\n"

    prompt = f"""Vazifa: Siz — {OWNER_NAME} ismli yigitsiz (erkak kishi).
Telegramda sizga kelgan xabarga oddiy, samimiy va jonli o'zbek tilida (og'zaki nutqqa mos qilib) javob bering.
O'zingizni bot yoki AI deb aslo aytmang.
Javobingiz 2-3 ta qisqa va aniq gapdan iborat bo'lsin.

{dialogue}Suhbatdosh: {clean_message}
{OWNER_NAME}:"""

    # 500 xatosiga qarshi avtomatik qayta urinish (3 martagacha)
    reply = ""
    for attempt in range(3):
        try:
            client = get_ai_client()
            response = client.models.generate_content(
                model=PRIMARY_MODEL,
                contents=prompt
            )
            if response and response.text:
                reply = response.text.strip()
                break
        except Exception as e:
            print(f"⚠️ Urinish {attempt+1} xatosi: {e}", flush=True)
            time.sleep(0.5)

    if reply:
        for p in [f"{OWNER_NAME}:", f"{OWNER_NAME} :", "Assistent:", "AI:"]:
            if reply.lower().startswith(p.lower()):
                reply = reply[len(p):].strip()

        if "sun'iy intellekt" in reply.lower() or "botman" in reply.lower():
            reply = "Hozir ozgina ishlarim bor edi, nima gaplar?"
    else:
        # Agar 3 marta urinib ham javob ololmasa, savolga mos tabiiy insoniy javob
        reply = "Xabaringni ko'rdim, hozir sal bandroq edim, birozdan keyin o'zim batafsil yozaman."

    user_data["history"].append({"role": "user", "text": clean_message})
    user_data["history"].append({"role": "model", "text": reply})

    return reply
