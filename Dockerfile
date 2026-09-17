FROM python:3.11-slim

WORKDIR /app

# Tizim paketlarini yangilash va ffmpeg o'rnatish
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libopus0 \
    && rm -rf /var/lib/apt/lists/*

# Ortiqcha kutubxonalarni o'rnatmasdan to'g'ridan-to'g'ri o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Xotiradagi barcha eski pyc keshlarini o'chirish
RUN find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

CMD ["python", "userbot.py"]
