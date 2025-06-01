from telegram.ext import Updater, CommandHandler, ApplicationBuilder, ContextTypes, MessageHandler, filters
import os
import re

async def check(update, context):
    await update.message.reply_text("I'm ready")

async def url_handler(update, context):
    await update.message.reply_text("I see")

def main():
    print("Starting datasamorybot...")
    token = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("check", check))
    app.add_handler(MessageHandler(filters.Entity("url"), url_handler))
    app.run_polling()
    print("Hello from datasamorybot!")

if __name__ == "__main__":
    main()
