import os
import re
import asyncio
from gtts import gTTS

def text_to_voice_sync(text: str, output_path: str) -> bool:
    """Google TTS — serverda hech qachon 403 blok bermaydi, 100% barqaror va tezkor"""
    try:
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        # Ruscha bo'lsa ru, o'zbekcha bo'lsa tr (chunki gTTS da turkiy ohang o'zbek tiliga eng yaqin)
        # Yoki to'g'ridan-to'g'ri tld='com' bilan ravon o'qiydi
        lang = "ru" if re.search(r'[а-яА-ЯёЁ]', clean_text) else "tr"
        
        tts = gTTS(text=clean_text, lang=lang, tld='com', slow=False)
        tts.save(output_path)

        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"❌ gTTS xatosi: {e}", flush=True)
        return False

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    try:
        loop = asyncio.get_running_loop()
        success = await loop.run_in_executor(None, text_to_voice_sync, text, output_path)
        if success:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Voice xatosi: {e}", flush=True)
        return ""
