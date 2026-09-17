import os
import edge_tts
import re
import traceback

def get_voice_for_text(text: str) -> str:
    # Ruscha so'zlar bo'lsa
    if re.search(r'[а-яА-ЯёЁ]', text):
        return "ru-RU-DmitryNeural"
    # O'zbek tili uchun (Sardor erkak ovozi yoki Madina)
    return "uz-UZ-SardorNeural"

async def text_to_voice_file(text: str, output_path: str = "reply_voice.ogg") -> str:
    """Matnni Telegram ovozli xabariga aylantirish"""
    try:
        # Matndagi smayliklarni va maxsus belgilarni tozalash (ovoz o'qishda buzilmasligi uchun)
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text)
        if not clean_text.strip():
            clean_text = text

        voice = get_voice_for_text(clean_text)
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(output_path)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Ovoz yaratish xatosi: {e}")
        traceback.print_exc()
        return ""
