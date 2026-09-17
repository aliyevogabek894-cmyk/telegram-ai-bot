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

        prompt = f"""Siz — {OWNER_NAME}siz (haqiqiy inson). Telegramda suhbatdoshingizning savoliga qarab, mazmunan to'liq, aqlli, samimiy va insoniy javob bering. O'zingizni bot yoki AI deb aytmang.

{dialogue}Suhbatdosh: {clean_message}
{OWNER_NAME}:"""

        # Retry mexanizmi bilan so'rov yuborish
        response = None
        for _ in range(2):
            try:
                response = client_instance.models.generate_content(
                    model=AI_MODEL_NAME,
                    contents=prompt
                )
                if response and response.text:
                    break
            except Exception:
                time.sleep(0.5)

        reply = response.text.strip() if (response and response.text) else "Eshitaman, nima gap?"

        # Prefikslarni tozalash
        for p in [f"{OWNER_NAME}:", f"{OWNER_NAME} :", "Assistent:", "AI:"]:
            if reply.lower().startswith(p.lower()):
                reply = reply[len(p):].strip()

        if "sun'iy intellekt" in reply.lower() or "botman" in reply.lower() or "ai model" in reply.lower():
            reply = "Hozir ozgina band edim, nima savol bor edi? Eshitaman."

        user_data["history"].append({"role": "user", "text": clean_message})
        user_data["history"].append({"role": "model", "text": reply})

        return reply

    except Exception as e:
        return "Eshitaman, ozgina band edim. Nima gaplar?"
