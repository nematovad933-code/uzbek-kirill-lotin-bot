"""
Telegram bot sozlamalari (Konfiguratsiya).
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# .env fayli mavjud bo'lsa, undan o'qib olish
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "9074930999:AAGV0D85ctHnoexLPz9sOB761Cq4q_uR-kU")

# Vaqtinchalik fayllar saqlanadigan papka
TEMP_DIR = os.path.join(BASE_DIR, "temp_files")

# Telegram Bot API maksimal fayl hajmi (20 MB)
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Standart Lotin alifbosi tahriri:
# 'new' - 2026-yilgi Yangi Tahrir (Ö ö, Ğ ğ, Ş ş, Ç ç)
# 'classic' - Amaldagi Klassik Tahrir (Oʻ oʻ, Gʻ gʻ, Sh sh, Ch ch)
DEFAULT_LATIN_VERSION = "new"

# Klassik tahrirda ishlatiladigan apostrof: 'oʻ' yoki 'o\''
DEFAULT_APOSTROPHE = "oʻ"
