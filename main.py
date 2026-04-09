import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

HOTSPOT_ID = "223173301"
CALLSIGN = "IU5CZN"


def get_status():
    url = f"https://api.brandmeister.network/v1.0/repeater/?action=profile&q={HOTSPOT_ID}"
    return requests.get(url, timeout=10).json()


def get_lastheard():
    url = f"https://api.brandmeister.network/v1.0/repeater/?action=lastheard&q={HOTSPOT_ID}"
    return requests.get(url, timeout=10).json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Bot IU5CZN attivo")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = get_status()
        stato = "🟢 Online" if data.get("status") == 1 else "🔴 Offline"
        await update.message.reply_text(f"{CALLSIGN} → {stato}")
    except:
        await update.message.reply_text("Errore status")


async def last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = get_lastheard()
        msg = "📻 Ultimi QSO:\n"
        for qso in data[:5]:
            msg += f"{qso['callsign']} → TG{qso['talkgroup']}\n"
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("Errore lastheard")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("last", last))

print("BOT DMR AVVIATO")

app.run_polling()
