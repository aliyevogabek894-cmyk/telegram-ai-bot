import io
import edge_tts
import re

def get_voice_for_text(text: str) -> str:
    if re.search(r'[а-яА-ЯёЁ]', text):
        return "ru-RU-DmitryNeural"
    return "uz-UZ-SardorNeural"

async def text_to_voice_bytes(text: str) -> io.BytesIO:
    """Matnni diskka yozmasdan, to'g'ridan-to'g'ri RAM (xotira) orqali juda tez ovozga aylantiradi"""
    try:
        # Emojilarni tozalash (tezlik uchun)
        clean_text = re.sub(r'[^\w\s\.,!\?\'"\-—:;]+', '', text).strip()
        if not clean_text:
            clean_text = text

        voice = get_voice_for_text(clean_text)
        
        # rate="+15%" — tabiiy va tezroq gapirish uchun (audio hajmi kichrayadi va tez yuboriladi)
        communicate = edge_tts.Communicate(clean_text, voice, rate="+15%")
        
        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
        
        audio_buffer.seek(0)
        audio_buffer.name = "voice.ogg"  # Telegram voice format
        return audio_buffer
    except Exception as e:
        print(f"❌ Tezkor ovoz xatosi: {e}")
        return None
