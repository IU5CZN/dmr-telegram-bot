import requests
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
HOTSPOT_ID = "223173301"
CALLSIGN = "IU5CZN"

last_status = None
last_qso = None
chat_id_global = None


def get_status():
    url = f"https://api.brandmeister.network/v1.0/repeater/?action=profile&q={HOTSPOT_ID}"
    return requests.get(url, timeout=10).json()


def get_lastheard():
    url = f"https://api.brandmeister.network/v1.0/repeater/?action=lastheard&q={HOTSPOT_ID}"
    return requests.get(url, timeout=10).json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_id_global
    chat_id_global = update.effective_chat.id
    await update.message.reply_text(f"📡 Monitor attivo IU5CZN")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_status()
    stato = "🟢 Online" if data.get("status") == 1 else "🔴 Offline"
    await update.message.reply_text(stato)


async def last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_lastheard()
    msg = ""
    for qso in data[:5]:
        msg += f"{qso['callsign']} → TG{qso['talkgroup']}\n"
    await update.message.reply_text(msg or "Nessun QSO")


async def monitor(app):
    global last_status, last_qso, chat_id_global

    while True:
        try:
            data = get_status()
            status = data.get("status")

            if last_status is None:
                last_status = status

            if status != last_status and chat_id_global:
                text = "🟢 ONLINE" if status == 1 else "🔴 OFFLINE"
                await app.bot.send_message(chat_id_global, text)
                last_status = status

            lh = get_lastheard()

            if lh:
                latest = lh[0]
                qso_id = f"{latest['callsign']}{latest['talkgroup']}"

                if qso_id != last_qso and chat_id_global:
                    await app.bot.send_message(
                        chat_id_global,
                        f"📡 {latest['callsign']} → TG{latest['talkgroup']}"
                    )
                    last_qso = qso_id

        except Exception as e:
            print("ERROR:", e)

        await asyncio.sleep(60)


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("last", last))

    asyncio.create_task(monitor(app))

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
