import os
import re
import edge_tts
import asyncio

def get_voice_for_text(text: str) -> str:
    if re.search(r'[а-яА-ЯёЁ]', text):
        return "ru-RU-DmitryNeural"
    return "uz-UZ-SardorNeural"

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    """Telegram uchun 100% mos OGG/Opus ovozli xabari yaratish"""
    try:
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        voice = get_voice_for_text(clean_text)
        
        # Audio yaratish
        communicate = edge_tts.Communicate(clean_text, voice, rate="+10%")
        await communicate.save(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Voice xatosi: {e}")
        return ""
