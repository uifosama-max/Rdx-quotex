import os
import yfinance as yf
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("8489267260:AAFrufA4wlyS_kkKfz8fiTILs52-7gtN3IQ")

running = False

def get_signal():
df = yf.download("EURUSD=X", interval="1m", period="1d")

df['support'] = df['Low'].rolling(20).min()
df['resistance'] = df['High'].rolling(20).max()

last = df.iloc[-1]

if last['Close'] <= last['support']:
    return "🟢 UP SIGNAL (Support)"
elif last['Close'] >= last['resistance']:
    return "🔴 DOWN SIGNAL (Resistance)"
else:
    return "⚪ NO TRADE ZONE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
keyboard = [["START BOT", "STOP BOT"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

await update.message.reply_text(
    "🔥 Quotex Signal Bot Ready!",
    reply_markup=reply_markup
)

async def signal_loop(context: ContextTypes.DEFAULT_TYPE):
global running

if running:
    signal = get_signal()
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f"📊 {signal}"
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
global running

text = update.message.text

if text == "START BOT":
    running = True
    context.job_queue.run_repeating(signal_loop, interval=60, first=1, chat_id=update.effective_chat.id)
    await update.message.reply_text("✅ Bot Started!")

elif text == "STOP BOT":
    running = False
    await update.message.reply_text("🛑 Bot Stopped!")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_buttons))

app.run_polling()
