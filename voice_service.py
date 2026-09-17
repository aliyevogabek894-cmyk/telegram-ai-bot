import os
import edge_tts
import re

# Tilni aniqlash va mos ovozni tanlash
def get_voice_for_text(text: str) -> str:
    # Ruscha harflar bo'lsa
    if re.search(r'[а-яА-ЯёЁ]', text):
        return "ru-RU-DmitryNeural"
    # O'zbek tili uchun erkak kishi ovozi (Sardor)
    return "uz-UZ-SardorNeural"

async def text_to_voice_file(text: str, output_path: str = "reply_voice.ogg") -> str:
    """Matnni Telegram voice (OGG/Opus) fayliga aylantiradi"""
    try:
        voice = get_voice_for_text(text)
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        print(f"❌ Ovoz yaratishda xatolik: {e}")
        return ""
