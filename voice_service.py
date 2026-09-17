import os
import re
import asyncio
import subprocess
from gtts import gTTS

def create_voice_sync(text: str, output_path: str) -> bool:
    """Google TTS orqali audio yaratib, ffmpeg bilan haqiqiy Telegram OGG/Opus ovoziga aylantirish"""
    temp_mp3 = output_path.replace(".ogg", ".mp3")
    try:
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        # Ruscha bo'lsa ru, o'zbekcha bo'lsa toza o'zbekcha / turkiy talaffuz
        lang = "ru" if re.search(r'[а-яА-ЯёЁ]', clean_text) else "uz"
        
        try:
            tts = gTTS(text=clean_text, lang=lang, slow=False)
            tts.save(temp_mp3)
        except Exception:
            # Agar 'uz' ba'zi hududda bo'lmasa, eng yaqin turkiy talaffuz
            tts = gTTS(text=clean_text, lang="tr", slow=False)
            tts.save(temp_mp3)

        # ffmpeg orqali Telegram Voice Note (OGG/Opus) formatiga o'girish (to'lqinli ovoz bo'lishi uchun)
        if os.path.exists(temp_mp3):
            cmd = f'ffmpeg -y -i "{temp_mp3}" -c:a libopus -b:a 32k -vbr on "{output_path}"'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Agar ogg muvaffaqiyatli chiqsa
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                try:
                    os.remove(temp_mp3)
                except Exception:
                    pass
                return True
            else:
                # Agar ffmpeg bo'lmasa, to'g'ridan-to'g'ri mp3 ni qoldiramiz
                if os.path.exists(temp_mp3):
                    os.rename(temp_mp3, output_path)
                    return True
        return False
    except Exception as e:
        print(f"❌ Ovoz yaratish xatosi: {e}", flush=True)
        return False

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    try:
        loop = asyncio.get_running_loop()
        ok = await loop.run_in_executor(None, create_voice_sync, text, output_path)
        if ok and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return ""
    except Exception as e:
        print(f"❌ Voice xatosi: {e}", flush=True)
        return ""
