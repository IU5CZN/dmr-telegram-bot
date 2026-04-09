import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

HOTSPOT_ID = "223173301"
CALLSIGN = "IU5CZN"


def get_status():
    url = f"https://api.brandmeister.network/v2/device/{HOTSPOT_ID}"
    r = requests.get(url, timeout=10)
    return r.json() if r.status_code == 200 else None


def get_lastheard():
    url = f"https://api.brandmeister.network/v2/repeater/{HOTSPOT_ID}/last-heard"
    r = requests.get(url, timeout=10)
    return r.json() if r.status_code == 200 else None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Bot IU5CZN attivo")


state = data.get("status", "unknown")

if str(state) == "1":
     stato = "🟢 Online"
elif str(state) == "0":
     stato = "🔴 Offline"
else:
     stato = "🟡 Sconosciuto"

await update.message.reply_text(f"{CALLSIGN} → {stato}")

except Exception as e:
await update.message.reply_text(f"Errore: {e}")


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
