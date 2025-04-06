
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === CONFIG ===

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')


QUEUE = []

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === HANDLERS ===
async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = update.message
    QUEUE.append((msg.chat_id, msg.message_id))
    await msg.reply_text(f"✅ Queued! Current queue: {len(QUEUE)}")

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
        logger.info(f"Forwarded message {message_id} from {chat_id}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to forward message {message_id}: {e}")

async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    QUEUE.clear()
    await update.message.reply_text("🗑️ Queue cleared.")

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(f"📦 Queue length: {len(QUEUE)}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive and ready.")

# === STARTUP LOG ===
async def on_startup(application: Application):
    logger.info("🚀 Bot started and ready.")

# === BOT APP ===
app = Application.builder().token(BOT_TOKEN).post_init(on_startup).build()

app.add_handler(MessageHandler(filters.ALL, add_to_queue))
app.add_handler(CommandHandler("clear", clear_queue))
app.add_handler(CommandHandler("status", show_status))
app.add_handler(CommandHandler("ping", ping))

app.job_queue.run_repeating(forward_from_queue, interval=180, first=10)  # every 3 minutes

app.run_polling()
