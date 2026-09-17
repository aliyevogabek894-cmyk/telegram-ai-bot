FROM python:3.11-slim

WORKDIR /app

# Audio va ffmpeg tizim paketlarini o'rnatish
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libopus0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "userbot.py"]
