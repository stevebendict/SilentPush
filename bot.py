
import os
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging

print(">>> DEBUG: Loading environment variables...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

print(f">>> BOT_TOKEN: {repr(BOT_TOKEN)}")
print(f">>> ADMIN_IDS: {repr(ADMIN_IDS)}")
print(f">>> TARGET_CHANNEL: {repr(TARGET_CHANNEL)}")

# Fallback to hardcoded values if env vars fail
if not BOT_TOKEN or not BOT_TOKEN.startswith("7780"):
    print("❌ BOT_TOKEN not loaded from env! Falling back to hardcoded.")
    BOT_TOKEN = "7780572044:AAHGLKvdqSvfZ9_ovScbqH3SpJ55wsvRAfs"
    ADMIN_IDS = [6043250029, 7732449589]
    TARGET_CHANNEL = "-1002618211021"
else:
    ADMIN_IDs = int(ADMIN_IDs)

QUEUE = []

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        # Log unauthorized access
        log_message = (
            "⛔ Unauthorized access attempt\n"
            f"👤 User ID: {user.id}\n"
            f"📛 Username: @{user.username if user.username else 'None'}\n"
            f"🕒 Time: {update.message.date}"
        )
        try:
            await context.bot.send_message(chat_id="-1002467983364", text=log_message)
        except Exception as e:
            logger.warning(f"⚠️ Failed to send audit log: {e}")
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
    if update.effective_user.id not in ADMIN_IDS:

        return
    QUEUE.clear()
    await update.message.reply_text("🗑️ Queue cleared.")

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:

        return
    await update.message.reply_text(f"📦 Queue length: {len(QUEUE)}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive and ready.")

async def on_startup(application: Application):
    logger.info("🚀 Bot started and ready.")

app = Application.builder().token(BOT_TOKEN).post_init(on_startup).build()

app.add_handler(MessageHandler(filters.ALL, add_to_queue))
app.add_handler(CommandHandler("clear", clear_queue))
app.add_handler(CommandHandler("status", show_status))
app.add_handler(CommandHandler("ping", ping))

app.job_queue.run_repeating(forward_from_queue, interval=180, first=10)

app.run_polling()
