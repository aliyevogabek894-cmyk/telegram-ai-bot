import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Asosiy kalitlar
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "gemini-2.5-flash").strip()

# Admin kontaktlari
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@maktab_admin").strip()
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "+998901234567").strip()

# Xavfsizlik va xarajat nazorati
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "1000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "800"))
CONVERSATION_HISTORY_LIMIT = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "6"))

# Knowledge base faylini o'qish
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base.json"

def load_knowledge_base() -> str:
    """Maktab ma'lumotlarini JSON faylidan matn ko'rinishida o'qiydi"""
    try:
        if KNOWLEDGE_BASE_PATH.exists():
            with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            logging.warning("knowledge_base.json fayli topilmadi!")
            return "{}"
    except Exception as e:
        logging.error(f"Knowledge base o'qishda xatolik: {e}")
        return "{}"

# Logging sozlamalari
LOG_FILE = BASE_DIR / "bot.log"
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MaktabAIBot")
