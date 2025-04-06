
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

QUEUE = []

logging.basicConfig(level=logging.INFO)

# === HANDLERS ===
async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = update.message
    QUEUE.append((msg.chat_id, msg.message_id))
    await msg.reply_text("✅ Queued!")

async def forward_from_queue(context: ContextTypes.DEFAULT_TYPE):
    if not QUEUE:
        return
    chat_id, message_id = QUEUE.pop(0)
    try:
        await context.bot.forward_message(
            chat_id=TARGET_CHANNEL,
            from_chat_id=chat_id,
            message_id=message_id
        )
    except Exception as e:
        print(f"⚠️ Failed to forward message {message_id}: {e}")

async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    QUEUE.clear()
    await update.message.reply_text("🗑️ Queue cleared.")

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(f"📦 Queue length: {len(QUEUE)}")

# === BOT APP ===
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, add_to_queue))
app.add_handler(CommandHandler("clear", clear_queue))
app.add_handler(CommandHandler("status", show_status))

app.job_queue.run_repeating(forward_from_queue, interval=180, first=10)  # every 3 minutes

app.run_polling()
