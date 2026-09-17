import os
import re
import asyncio
import edge_tts

# O'zbek tili uchun O'G'IL BOLA rasmiy diktor ovozi (Sardor)
VOICE_UZBEK_MALE = "uz-UZ-SardorNeural"
VOICE_RUSSIAN_MALE = "ru-RU-DmitryNeural"

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    """Toza o'zbek tilida erkak kishi (Sardor) ovozi bilan audio yaratish"""
    try:
        # Smayliklar va keraksiz belgilarni tozalash (talaffuz o'ta toza chiqishi uchun)
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        # Ruscha bo'lsa Dmitry, o'zbekcha bo'lsa 100% Sardor
        if re.search(r'[а-яА-ЯёЁ]', clean_text):
            voice = VOICE_RUSSIAN_MALE
        else:
            voice = VOICE_UZBEK_MALE

        # rate="+5%", pitch="-2Hz" (vazminroq, yoqimli erkak ovozi uchun)
        communicate = edge_tts.Communicate(clean_text, voice, rate="+5%", pitch="-2Hz")
        await communicate.save(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Ovoz yaratishda xato: {e}")
        return ""
