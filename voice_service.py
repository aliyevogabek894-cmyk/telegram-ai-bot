import asyncio
import os
import re
import sys
import subprocess
import edge_tts
from gtts import gTTS

# UTF-8 chiqishini ta'minlash (Windows va Linux uchun)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

async def generate_edge_tts(text: str, voice: str, output_path: str) -> bool:
    """Edge-TTS orqali tabiiy o'g'il bola ovozini yaratish (uz-UZ-SardorNeural)"""
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"[EDGE-TTS ERROR] {voice}: {e}", flush=True)
        return False

def convert_to_opus_sync(input_mp3: str, output_ogg: str) -> bool:
    """ffmpeg orqali Telegram Voice Note (.ogg Opus) formatiga o'tkazish"""
    try:
        cmd = f'ffmpeg -y -i "{input_mp3}" -c:a libopus -b:a 32k -vbr on "{output_ogg}"'
        res = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_ogg) and os.path.getsize(output_ogg) > 0:
            return True
    except Exception as e:
        print(f"[FFMPEG WARN] {e}", flush=True)
    return False

def fallback_gtts_sync(text: str, output_path: str) -> bool:
    """Favqulodda zaxira (agar Microsoft serveri vaqtinchalik javob bermasa)"""
    raw_mp3 = output_path.replace(".ogg", "_fb_raw.mp3")
    try:
        lang = "ru" if re.search(r'[а-яА-ЯёЁ]', text) else "tr"
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(raw_mp3)

        if os.path.exists(raw_mp3) and os.path.getsize(raw_mp3) > 0:
            cmd = f'ffmpeg -y -i "{raw_mp3}" -af "asetrate=24000*0.82,atempo=1.22" -c:a libopus -b:a 32k -vbr on "{output_path}"'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                try:
                    os.remove(raw_mp3)
                except Exception:
                    pass
                return True

            if os.path.exists(raw_mp3):
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception:
                        pass
                os.rename(raw_mp3, output_path)
                return True
    except Exception as e:
        print(f"[GTTS ERROR] {e}", flush=True)
    return False

async def text_to_voice_file(text: str, output_path: str = "voice.ogg") -> str:
    """O'zbek tilida toza talaffuzli erkak kishi (Sardor) ovozli xabarini yaratish"""
    try:
        # 1. Matnni tozalash
        clean_text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', clean_text).strip()
        if not clean_text:
            clean_text = text.strip()

        # 2. Ovoz tanlash: Ruscha bo'lsa Dmitry, o'zbekcha bo'lsa Sardor (haqiqiy o'zbek o'g'il bola)
        is_russian = bool(re.search(r'[а-яА-ЯёЁ]', clean_text))
        voice = "ru-RU-DmitryNeural" if is_russian else "uz-UZ-SardorNeural"

        temp_mp3 = output_path.replace(".ogg", "_temp.mp3")
        if os.path.exists(temp_mp3):
            try:
                os.remove(temp_mp3)
            except Exception:
                pass

        # 3. Asosiy: Edge-TTS (Sardor - sof o'zbek tili talaffuzi)
        success = await generate_edge_tts(clean_text, voice, temp_mp3)

        if success and os.path.exists(temp_mp3) and os.path.getsize(temp_mp3) > 0:
            # ffmpeg orqali OGG Opus ga aylantirish (Docker/Renderda 100% ishlaydi)
            loop = asyncio.get_running_loop()
            converted = await loop.run_in_executor(None, convert_to_opus_sync, temp_mp3, output_path)

            if converted and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                try:
                    os.remove(temp_mp3)
                except Exception:
                    pass
                return output_path
            else:
                # Agar ffmpeg bo'lmasa, mp3 faylni output_path ga o'tkazib yuboramiz
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception:
                        pass
                os.rename(temp_mp3, output_path)
                return output_path

        # 4. Zaxira: Agar Edge-TTS vaqtinchalik ishlamay qolsa
        print("[WARN] Edge-TTS ishlamadi, zaxira tizim ishga tushirilyapti...", flush=True)
        loop = asyncio.get_running_loop()
        fb_ok = await loop.run_in_executor(None, fallback_gtts_sync, clean_text, output_path)
        if fb_ok and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path

        return ""
    except Exception as e:
        print(f"[VOICE ERROR] Umumiy xato: {e}", flush=True)
        return ""
