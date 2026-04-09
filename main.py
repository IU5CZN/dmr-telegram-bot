import os
import threading
import paho.mqtt.client as mqtt

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("TOKEN")

HOTSPOT_ID = "223173301"
CALLSIGN = "IU5CZN"

last_qso = None
last_tg = None

# ======================
# MQTT SETUP (BrandMeister)
# ======================

MQTT_BROKER = "broker.brandmeister.network"
MQTT_PORT = 1883


def on_connect(client, userdata, flags, rc):
    print("MQTT connesso:", rc)

    # ascolti generici DMR
    client.subscribe("dmr/#")


def on_message(client, userdata, msg):
    global last_qso, last_tg

    try:
        payload = msg.payload.decode(errors="ignore")

        # filtra solo traffico utile DMR
        if "talkgroup" in payload.lower() or "tg" in payload.lower():

            last_qso = payload

            # prova estrazione TG semplice
            import re
            tg = re.findall(r"\b\d{2,8}\b", payload)

            if tg:
                last_tg = tg[0]

    except Exception as e:
        print("MQTT error:", e)


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


def start_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()


threading.Thread(target=start_mqtt, daemon=True).start()

# ======================
# TELEGRAM BOT
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Bot IU5CZN attivo (MQTT live)")


async def tg(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if last_qso:
        msg = f"📡 LIVE DMR IU5CZN\n"

        if last_tg:
            msg += f"TG Attivo: {last_tg}\n\n"

        msg += f"Dati:\n{last_qso}"

        await update.message.reply_text(msg)

    else:
        await update.message.reply_text("Nessun traffico rilevato ancora")


# ======================
# START APP
# ======================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("tg", tg))

print("BOT AVVIATO")

app.run_polling()
