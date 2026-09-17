import time
import os
from typing import Dict
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
AI_MODEL_NAME = "gemma-4-26b-a4b-it"
OWNER_NAME = "Og'abek"

user_conversations: Dict[int, Dict] = {}
SESSION_TIMEOUT_SECONDS = 3600

client_instance = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

async def generate_ai_response(user_id: int, user_message: str) -> str:
    try:
        if not client_instance:
            return "Salom, yaxshimisiz?"

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
Ovozli xabar qilib o'qilishi uchun qulay, ravon so'zlarni ishlating.
O'zingizni sun'iy intellekt yoki bot deb aslo aytmang.
Javobingiz 2-3 ta qisqa va aniq gapdan iborat bo'lsin.

{dialogue}Suhbatdosh: {clean_message}
{OWNER_NAME}:"""

        response = client_instance.models.generate_content(
            model=AI_MODEL_NAME,
            contents=prompt
        )

        reply = response.text.strip() if (response and response.text) else "Eshitaman, nima gap?"

        for p in [f"{OWNER_NAME}:", f"{OWNER_NAME} :", "Assistent:", "AI:"]:
            if reply.lower().startswith(p.lower()):
                reply = reply[len(p):].strip()

        if "sun'iy intellekt" in reply.lower() or "botman" in reply.lower():
            reply = "Hozir ozgina ishlarim bor edi, nima gaplar?"

        user_data["history"].append({"role": "user", "text": clean_message})
        user_data["history"].append({"role": "model", "text": reply})

        return reply

    except Exception as e:
        print(f"❌ AI Xatolik: {e}")
        return "Eshitaman, tinchlikmi? Nima gaplar?"
