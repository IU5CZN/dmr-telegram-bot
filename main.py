import requests
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
HOTSPOT_ID = "223173301"
CALLSIGN = "IU5CZN"

CHECK_INTERVAL = 60
NOTIFY_QSO = True
FILTER_TG = [2220, 9]

last_status = None
last_qso_id = None
chat_id_global = None

def get_status():
    url = f"https://api.brandmeister.network/v1.0/repeater/?action=profile&q={HOTSPOT_ID}"
    return requests.get(url).json()

def get_lastheard():
    url = f"https://api.brandmeister.network/v1.0/repeater/?action=lastheard&q={HOTSPOT_ID}"
    return requests.get(url).json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_id_global
    chat_id_global = update.effective_chat.id
    await update.message.reply_text(f"📡 Monitor attivo per {CALLSIGN}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_status()
    stato = "🟢 Online" if data.get("status") == 1 else "🔴 Offline"
    await update.message.reply_text(f"{CALLSIGN} → {stato}")

async def last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_lastheard()
    msg = "📻 Ultimi QSO:\n"
    for qso in data[:5]:
        msg += f"{qso['callsign']} → TG{qso['talkgroup']}\n"
    await update.message.reply_text(msg)

async def tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_lastheard()
    tg_list = list(set([qso['talkgroup'] for qso in data[:10]]))
    msg = "📡 TG attivi:\n"
    for tg in tg_list:
        msg += f"- TG{tg}\n"
    await update.message.reply_text(msg)

async def monitor(app):
    global last_status, last_qso_id

    while True:
        try:
            status_data = get_status()
            current_status = status_data.get("status")

            if last_status is None:
                last_status = current_status

            if current_status != last_status:
                if chat_id_global:
                    msg = f"🟢 {CALLSIGN} ONLINE" if current_status == 1 else f"🔴 {CALLSIGN} OFFLINE"
                    await app.bot.send_message(chat_id=chat_id_global, text=msg)

                last_status = current_status

            if NOTIFY_QSO:
                data = get_lastheard()

                if data:
                    latest = data[0]
                    qso_id = f"{latest['callsign']}-{latest['talkgroup']}"

                    if last_qso_id is None:
                        last_qso_id = qso_id

                    if qso_id != last_qso_id:
                        tg = latest['talkgroup']

                        if not FILTER_TG or tg in FILTER_TG:
                            msg = f"📡 {latest['callsign']} → TG{tg}"
                            if chat_id_global:
                                await app.bot.send_message(chat_id=chat_id_global, text=msg)

                        last_qso_id = qso_id

        except Exception as e:
            print(e)

        await asyncio.sleep(CHECK_INTERVAL)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("last", last))
app.add_handler(CommandHandler("tg", tg))



app.run_polling()
async def main():
    asyncio.create_task(monitor(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
