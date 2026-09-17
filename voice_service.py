import os
import re
import asyncio
import edge_tts

# Haqiqiy o'zbek yigitining rasmiy ovozi
VOICE_MALE_UZ = "uz-UZ-SardorNeural"
VOICE_MALE_RU = "ru-RU-DmitryNeural"

def get_voice(text: str) -> str:
    if re.search(r'[а-яА-ЯёЁ]', text):
        return VOICE_MALE_RU
    return VOICE_MALE_UZ

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    """Haqiqiy o'zbek o'g'il bola (Sardor) ovozi bilan toza va ravon audio yaratish"""
    try:
        # Smaylik va maxsus belgilarni tozalash
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        voice = get_voice(clean_text)
        
        # pitch="-1Hz", rate="+5%" — tabiiy erkak kishi ohangi
        communicate = edge_tts.Communicate(clean_text, voice, rate="+5%", pitch="-1Hz")
        await communicate.save(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Ovoz xatosi: {e}", flush=True)
        return ""
