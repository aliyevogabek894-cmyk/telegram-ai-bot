import os
import re
import asyncio
import edge_tts

# O'zbek tili uchun O'G'IL BOLA ovozi (Sardor)
VOICE_UZBEK_MALE = "uz-UZ-SardorNeural"
# Rus tili uchun erkak ovozi (Dmitry)
VOICE_RUSSIAN_MALE = "ru-RU-DmitryNeural"

def get_male_voice(text: str) -> str:
    """Faqat o'g'il bola (erkak) ovozini tanlaydi"""
    if re.search(r'[а-яА-ЯёЁ]', text):
        return VOICE_RUSSIAN_MALE
    # O'zbekcha erkak kishi ovozi
    return VOICE_UZBEK_MALE

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    """Toza o'zbek tilida o'g'il bola ovozi bilan audio yaratish"""
    try:
        # Smayliklarni tozalash (talaffuz buzilmasligi uchun)
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        voice = get_male_voice(clean_text)
        
        # rate="+10%" — tabiiy va jonli tezlikda gapirish
        communicate = edge_tts.Communicate(clean_text, voice, rate="+10%")
        await communicate.save(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Ovoz xatosi: {e}")
        return ""
