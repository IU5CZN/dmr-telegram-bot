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


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = f"https://api.brandmeister.network/v1.0/repeater/?action=profile&q={HOTSPOT_ID}"
        r = requests.get(url, timeout=10)

        print("BM RAW RESPONSE:", r.text)  # DEBUG corretto

        try:
            data = r.json()
        except:
            await update.message.reply_text("⚠️ Risposta non JSON da BrandMeister")
            return

        if not data:
            await update.message.reply_text("⚠️ Nessun dato disponibile")
            return

        status_val = data.get("status", "unknown")

        if str(status_val) == "1":
            stato = "🟢 Online"
        elif str(status_val) == "0":
            stato = "🔴 Offline"
        else:
            stato = f"🟡 Sconosciuto ({status_val})"

        await update.message.reply_text(f"📡 IU5CZN → {stato}")

    except Exception as e:
        await update.message.reply_text(f"❌ Errore: {e}")
        
print("BM RAW RESPONSE:", r.text)

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
