# 🎓 Maktab AI Avtomatik Javob Telegram Boti

Ushbu loyiha maktab yoki o'quv markazi uchun mo'ljallangan, sun'iy intellekt (Google Gemini) bilan integratsiya qilingan aqlli Telegram botdir.

## 📁 Loyiha Tuzilmasi
- **`main.py`** — Botni ishga tushiruvchi asosiy fayl.
- **`config.py`** — Sozlamalar va `.env` o'qish.
- **`ai_service.py`** — AI logikasi, xotira (kontekst) va xarajat cheklovlari.
- **`handlers.py`** — Telegram xabarlarini qayta ishlash.
- **`knowledge_base.json`** — Maktab ma'lumotlari bazasi (narxlar, manzillar, qoidalar).
- **`.env`** — Maxfiy API kalitlar.
- **`requirements.txt`** — Kutubxonalar.

---

## ⚙️ O'rnatish va Ishga Tushirish (Windows)

1. **Virtual muhitni faollashtiring:**
   ```powershell
   .\venv\Scripts\Activate
   ```

2. **Kutubxonalarni o'rnating:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **`.env` fayliga kalitlarni yozing:**
   - `TELEGRAM_BOT_TOKEN`: BotFather dan olingan token.
   - `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com) dan olingan kalit.

4. **Botni ishga tushiring:**
   ```powershell
   python main.py
   ```

---

## 🧪 Test qilish uchun 10 ta Savol va Kutiladigan Natija

1. **Salomlashish va erkin suhbat:**
   - *Savol:* `Assalomu alaykum, yaxshimisiz?`
   - *Natija:* Muloyim alik oladi va o'zini tanishtiradi.

2. **Narxlar haqida:**
   - *Savol:* `1-sinf uchun oylik to'lov qancha va unga nimalar kiradi?`
   - *Natija:* `knowledge_base.json` dagi 3 500 000 so'm, ovqatlanish va to'garaklar kirishini aytadi.

3. **Chegirmalar:**
   - *Savol:* `2 ta farzandim bor, chegirma bormi?`
   - *Natija:* 2-farzand uchun 10% chegirma borligini tushuntiradi.

4. **Ovqatlanish va transport:**
   - *Savol:* `Maktabda ovqat beriladimi va avtobus bormi?`
   - *Natija:* Kuniga 3 mahal issiq ovqat va marshrut xizmati borligini aytadi.

5. **Manzil va mo'ljal:**
   - *Savol:* `Maktab qayerda joylashgan?`
   - *Natija:* Toshkent sh., Chilonzor tumani, Bunyodkor ko'chasi 15-uy (Mirzo Ulug'bek metrosi) deb aniq beradi.

6. **Kontekst (suhbat davomiyligi):**
   - *1-savol:* `To'garaklar bormi?`
   - *2-savol:* `Ularning ichida robototexnika ham bormi?`
   - *Natija:* Avvalgi savolni eslab, robototexnika borligini tasdiqlaydi.

7. **Bazada yo'q ma'lumot (Yolg'on to'qimaslik testi):**
   - *Savol:* `Maktabingizda basseyn yoki suzish havzasi bormi?`
   - *Natija:* Yolg'on to'qimaydi, bazada yo'qligini aytib, ma'muriyat bilan bog'lanishni tavsiya qiladi.

8. **Rus tilida savol:**
   - *Savol:* `Здравствуйте! Сколько стоит обучение в 6 классе?`
   - *Natija:* Rus tilida 4 000 000 so'm ekanligini chiroyli tushuntiradi.

9. **Ingliz tilida savol:**
   - *Savol:* `What are the school hours?`
   - *Natija:* Ingliz tilida dars vaqtlari (09:00 - 16:30) haqida javob beradi.

10. **Tarixni tozalash:**
    - *Buyruq:* `/clear`
    - *Natija:* Suhbat xotirasini tozalaydi.
