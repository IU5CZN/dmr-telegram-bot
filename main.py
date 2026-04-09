import os
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("TOKEN")

async def start(update, context):
    await update.message.reply_text("Bot OK 👍")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

print("BOT AVVIATO")

app.run_polling()
