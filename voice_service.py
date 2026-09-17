import os
import re
import asyncio
import subprocess
from gtts import gTTS

def create_voice_sync(text: str, output_path: str) -> bool:
    """Google TTS ovozini erkak kishi (o'g'il bola) tembriga o'girish va Telegram OGG Opus yaratish"""
    raw_mp3 = output_path.replace(".ogg", "_raw.mp3")
    try:
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        lang = "ru" if re.search(r'[а-яА-ЯёЁ]', clean_text) else "tr"
        
        # 1. Boshlang'ich audio
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        tts.save(raw_mp3)

        if os.path.exists(raw_mp3):
            # 2. ffmpeg orqali ovoz chastotasini erkak kishi tembriga pasaytirish (pitch shift):
            # asetrate=24000*0.83 (ovozni erkakchasiga yo'g'onlashtiradi) va atempo=1.2 (tezlikni tabiiy qiladi)
            # -c:a libopus (Telegram haqiqiy Voice Note standarti)
            cmd = (
                f'ffmpeg -y -i "{raw_mp3}" '
                f'-af "asetrate=24000*0.84,atempo=1.19" '
                f'-c:a libopus -b:a 32k -vbr on "{output_path}"'
            )
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Tozalash
            try:
                os.remove(raw_mp3)
            except Exception:
                pass

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True
        return False
    except Exception as e:
        print(f"❌ Ovoz xatosi: {e}", flush=True)
        return False

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    try:
        loop = asyncio.get_running_loop()
        ok = await loop.run_in_executor(None, create_voice_sync, text, output_path)
        if ok:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Voice xatosi: {e}", flush=True)
        return ""
