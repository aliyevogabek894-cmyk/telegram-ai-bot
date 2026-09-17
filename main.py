import sys
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import config
import handlers

def main():
    """Botni ishga tushirish funksiyasi"""
    print("==================================================")
    print("🤖 Maktab AI Telegram Boti ishga tushmoqda...")
    print("==================================================")

    # Token tekshiruvi
    if not config.TELEGRAM_BOT_TOKEN or config.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        print("❌ XATOLIK: TELEGRAM_BOT_TOKEN topilmadi!")
        print("Iltimos, .env faylini ochib, TELEGRAM_BOT_TOKEN qiymatini to'g'ri kiriting.")
        sys.exit(1)

    # Application qurish
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Buyruqlarni ro'yxatdan o'tkazish
    app.add_handler(CommandHandler("start", handlers.start_command))
    app.add_handler(CommandHandler("help", handlers.help_command))
    app.add_handler(CommandHandler("clear", handlers.clear_command))

    # Matnli xabarlarni qayta ishlash
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))

    # Xatoliklarni ushlab qoluvchi handler
    app.add_error_handler(handlers.error_handler)

    print("✅ Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda!")
    print("Botni to'xtatish uchun: Ctrl + C bosing.")
    print("==================================================")

    # Botni ishga tushirish (Polling rejimida)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
