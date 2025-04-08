
import os
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging

print(">>> DEBUG: Loading environment variables...")

# ✅ Hardcoded config
BOT_TOKEN = "7728785789:AAEK7O-NBdl4XD1DhtpBM_oeGb48Ptl7ZpA"
ADMIN_IDS = [6043250029, 7664906760]
TARGET_CHANNEL_PUBLIC = "-1002500055359"     # Public Channel
TARGET_CHANNEL_PRIVATE = "-1002509063620"    # Paid Private Channel

# ✅ Optional debug print
print(f">>> BOT_TOKEN: {repr(BOT_TOKEN)}")
print(f">>> ADMIN_IDS: {repr(ADMIN_IDS)}")
print(f">>> PUBLIC CHANNEL ID: {TARGET_CHANNEL_PUBLIC}")
print(f">>> PRIVATE CHANNEL ID: {TARGET_CHANNEL_PRIVATE}")


QUEUE = []  # Each item: (chat_id, message_id, media_type, duration)

PUBLIC_POST_COUNTER = 0  # Track how many times we've posted to public channel

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

from datetime import timezone  # ✅ Move this to top with other imports

async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in ADMIN_IDS:
        # Log unauthorized access with formatted HTML message
        log_message = (
            "<b>🚨 UNAUTHORIZED ACCESS ATTEMPT</b>\n\n"
            f"👤 <b>User ID:</b> <code>{user.id}</code>\n"
            f"📛 <b>Username:</b> @{user.username if user.username else 'None'}\n"
            f"🕒 <b>Time:</b> <i>{update.message.date.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"
        )
        try:
            await context.bot.send_message(
                chat_id="-1002467983364",  # Your audit group ID
                text=log_message,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to send audit log: {e}")
            print(f"❌ Could not send unauthorized log to group: {e}")
        return

    msg = update.message
    media_type = None
duration = 0

if msg.video:
    media_type = "video"
    duration = msg.video.duration
elif msg.photo:
    media_type = "photo"
elif msg.document:
    media_type = "document"
elif msg.text:
    media_type = "text"

QUEUE.append((msg.chat_id, msg.message_id, media_type, duration))

    await msg.reply_text(f"✅ Queued! Current queue: {len(QUEUE)}")
    logger.info(f"✅ Queued by admin {update.effective_user.id}")


async def copy_from_queue(context: ContextTypes.DEFAULT_TYPE):
    global PUBLIC_POST_COUNTER

    if not QUEUE:
        return

    chat_id, message_id, media_type, duration = QUEUE.pop(0)

    send_to_public = True
    send_to_private = True

    # Restrict public posts if video is too long
    if media_type == "video" and duration > 60:
        send_to_public = False

    targets = []
    if send_to_private:
        targets.append(TARGET_CHANNEL_PRIVATE)
    if send_to_public:
        targets.append(TARGET_CHANNEL_PUBLIC)

    for target in targets:
        try:
            await context.bot.copy_message(
                chat_id=target,
                from_chat_id=chat_id,
                message_id=message_id
            )
            logger.info(f"✅ Copied message {message_id} to {target}")

            # Track public posts and auto-promo every 10th
            if target == TARGET_CHANNEL_PUBLIC:
                PUBLIC_POST_COUNTER += 1
                print(f"📊 Public post count: {PUBLIC_POST_COUNTER}")
                if PUBLIC_POST_COUNTER >= 10:
                    try:
                        await context.bot.send_message(
                            chat_id=TARGET_CHANNEL_PUBLIC,
                            text="🔥 <b>Want the full uncensored?</b>\n👉 <a href='https://t.me/+FCugUePRvK0zN2U9'>Join the VIP Vault Here</a>",
                            parse_mode="HTML",
                            disable_web_page_preview=True
                        )
                        logger.info("📢 Sent promo message to public channel")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to send promo: {e}")
                    PUBLIC_POST_COUNTER = 0  # Reset
        except Exception as e:
            logger.warning(f"⚠️ Failed to send to {target}: {e}")
            print(f"❌ Copy error to {target}: {e}")



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

# COMMANDS FIRST
app.add_handler(CommandHandler("clear", clear_queue))
app.add_handler(CommandHandler("status", show_status))
app.add_handler(CommandHandler("ping", ping))

# QUEUE EVERYTHING ELSE (non-command messages)
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), add_to_queue))
app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, add_to_queue))
# Catch-all fallback for any message type not already handled
app.add_handler(MessageHandler(filters.ALL, add_to_queue))


app.job_queue.run_repeating(copy_from_queue, interval=60, first=10)

app.run_polling()
