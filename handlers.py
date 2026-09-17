from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import config
from ai_service import generate_ai_response, clear_user_history

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start buyrug'i bosilganda xush kelibsiz xabari"""
    user_name = update.effective_user.first_name or "Hurmatli foydalanuvchi"
    text = (
        f"Assalomu alaykum, {user_name}! 👋\n\n"
        f"Men **Kelajak Ziyo Xususiy Maktabi**ning sun'iy intellekt yordamchisiman.\n\n"
        f"Sizga quyidagi masalalarda yordam bera olaman:\n"
        f"🔹 Maktab qabuli va imtihonlar\n"
        f"🔹 O'qish narxlari va to'lov shartlari\n"
        f"🔹 Dars jadvali, fanlar va to'garaklar\n"
        f"🔹 Maktab manzili va transport xizmati\n\n"
        f"Savolingizni to'g'ridan-to'g'ri yozib yuborishingiz mumkin! ✍️\n\n"
        f"ℹ️ /help — Yordam\n"
        f"🧹 /clear — Suhbat tarixini tozalash"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help buyrug'i"""
    text = (
        "💡 **Botdan foydalanish bo'yicha qo'llanma:**\n\n"
        "• Savollaringizni oddiy inson bilan gaplashgandek erkin yozing.\n"
        "• Bot o'zbek, rus va ingliz tillarida javob bera oladi.\n"
        "• Agar yangi mavzuda gaplashmoqchi bo'lsangiz, /clear buyrug'ini bosing.\n\n"
        f"📞 **Ma'muriyat bilan bog'lanish:**\n"
        f"Telegram: {config.ADMIN_USERNAME}\n"
        f"Telefon: {config.ADMIN_PHONE}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/clear buyrug'i orqali xotirani tozalash"""
    user_id = update.effective_user.id
    clear_user_history(user_id)
    await update.message.reply_text("🧹 Suhbat tarixi tozalandi. Yangi savollaringizni berishingiz mumkin!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi yozgan barcha matnli xabarlarni qabul qilib, AI orqali javob qaytarish"""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    user_text = update.message.text.strip()
    user_name = update.effective_user.full_name

    config.logger.info(f"Yangi xabar [{user_id} - {user_name}]: {user_text}")

    # Telegramda "yozmoqda..." (typing) holatini ko'rsatish
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # AI dan javob olish
    reply_text = await generate_ai_response(user_id, user_text)

    # Foydalanuvchiga javob qaytarish
    try:
        await update.message.reply_text(reply_text, parse_mode="Markdown")
    except Exception:
        # Agar javob ichida Markdown simvollari bilan bog'liq xato bo'lsa, oddiy matn qilib yuboramiz
        await update.message.reply_text(reply_text)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Kutilmagan xatoliklarni qayd qilish"""
    config.logger.error(f"Telegram Handler xatosi: {context.error}", exc_info=context.error)
