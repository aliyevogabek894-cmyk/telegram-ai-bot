import time
import os
import re
import sys
from typing import Dict
from google import genai
from dotenv import load_dotenv

load_dotenv()

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OWNER_NAME = "Og'abek"

# Limitga tushsa keyingi modelga o'tuvchi zanjir
AI_MODELS = [
    "gemini-flash-lite-latest",   # 1-chi: eng ko'p limit
    "gemini-3.5-flash-lite",      # 2-chi: zaxira lite
    "gemini-3.1-flash-lite",      # 3-chi: yana lite
    "gemini-3.5-flash",           # 4-chi: to'liq flash
    "gemini-3.8-flash",           # 5-chi: so'nggi avlod
]

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
Telegramda sizga kelgan xabarga toza, dona-dona, ravon va tushunarli o'zbek tilida javob bering.
Ovozli xabar qilib o'qilishi uchun so'zlarni sodda, imloviy xatosiz va o'zbek adabiy tilida yozing.
Smayliklar (emojilar), g'alati qisqartmalar va ortiqcha belgilarni umuman ishlatmang.
O'zingizni bot yoki AI deb aslo aytmang. Yigit kishi sifatida samimiy va erkin gapiring.
Javobingiz 2 ta yoki 3 ta qisqa va aniq gapdan oshmasin.

{dialogue}Suhbatdosh: {clean_message}
{OWNER_NAME}:"""

    reply = ""
    client = get_ai_client()

    for model_name in AI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                reply = response.text.strip()
                print(f"[AI OK] Model: {model_name}", flush=True)
                break
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                print(f"[AI QUOTA] {model_name} limiti tugadi, keyingiga o'tilmoqda...", flush=True)
                continue
            elif "503" in err_str or "UNAVAILABLE" in err_str:
                print(f"[AI UNAVAIL] {model_name} mavjud emas, keyingiga o'tilmoqda...", flush=True)
                continue
            else:
                print(f"[AI ERROR] {model_name}: {err_str[:100]}", flush=True)
                continue

    if reply:
        for p in [f"{OWNER_NAME}:", f"{OWNER_NAME} :", "Assistent:", "AI:"]:
            if reply.lower().startswith(p.lower()):
                reply = reply[len(p):].strip()

        # Emojilarni olib tashlash (TTS toza o'qishi uchun)
        reply = re.sub(r'[\U00010000-\U0010ffff]', '', reply).strip()

        if "sun'iy intellekt" in reply.lower() or "botman" in reply.lower() or "ai" == reply.lower().strip():
            reply = "Hozir ozgina ishlarim bor edi, nima gaplar?"
    else:
        reply = "Xabaringni oldim, hozir bandroq edim. Birozdan keyin o'zim yozaman."

    user_data["history"].append({"role": "user", "text": clean_message})
    user_data["history"].append({"role": "model", "text": reply})

    return reply
