import os
import edge_tts
import re

def get_voice_for_text(text: str) -> str:
    if re.search(r'[а-яА-ЯёЁ]', text):
        return "ru-RU-DmitryNeural"
    return "uz-UZ-SardorNeural"

async def text_to_voice_file(text: str, output_path: str = "reply_voice.ogg") -> str:
    """Matndan to'g'ridan-to'g'ri Telegram ovozli faylini yaratish"""
    try:
        # Smayliklarni tozalaymiz
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        voice = get_voice_for_text(clean_text)
        communicate = edge_tts.Communicate(clean_text, voice, rate="+15%")
        await communicate.save(output_path)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Ovoz xatosi: {e}")
        return ""
