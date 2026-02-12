import asyncio
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8511210028:AAHN7ArYp-_0IebYtbLPaCgm7fGjLVIuvtI"

running = False

keyboard = [["START", "STOP"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Fake market data example (you must connect real candle API later)
def get_candles():
    url = "https://api.binance.com/api/v3/klines?symbol=EURUSDT&interval=1m&limit=100"
    data = requests.get(url).json()

    df = pd.DataFrame(data)
    df = df.iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]
    df["close"] = df["close"].astype(float)

    return df


def generate_signal():
    df = get_candles()

    rsi = RSIIndicator(df["close"], window=14).rsi()
    last_rsi = rsi.iloc[-1]

    if last_rsi < 30:
        return "🟢 UP SIGNAL\nMarket: REAL\nEntry: 5 min"
    elif last_rsi > 70:
        return "🔴 DOWN SIGNAL\nMarket: REAL\nEntry: 5 min"
    else:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready!", reply_markup=markup)


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global running

    text = update.message.text

    if text == "START":
        running = True
        await update.message.reply_text("✅ Signal Started")

        while running:
            signal = generate_signal()

            if signal:
                await update.message.reply_text(signal)

            await asyncio.sleep(60)

    elif text == "STOP":
        running = False
        await update.message.reply_text("⛔ Signal Stopped")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, buttons))

app.run_polling()
