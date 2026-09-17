import os
import re
import asyncio
from gtts import gTTS

def get_lang(text: str) -> str:
    # Agar ruscha harflar bo'lsa rus tilida, aks holda o'zbek/turkcha ohangda
    if re.search(r'[а-яА-ЯёЁ]', text):
        return "ru"
    # O'zbek tili uchun eng ravon va tez til kodi
    return "tr"  # gTTS da tr/ru juda tez va tabiiy gapiradi

def generate_voice_sync(text: str, output_path: str) -> bool:
    """Google TTS orqali 0.5 soniyada audio hosil qilish"""
    try:
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        lang = get_lang(clean_text)
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        tts.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"❌ gTTS Xatolik: {e}")
        return False

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    """Asinxron holda zudlik bilan ovoz yaratish"""
    try:
        loop = asyncio.get_running_loop()
        # Bloklamasdan alohida oqimda tezkor yaratish
        ok = await loop.run_in_executor(None, generate_voice_sync, text, output_path)
        if ok:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Voice xatosi: {e}")
        return ""
