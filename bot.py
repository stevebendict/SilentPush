
import os
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging
import random  # 👈 Add this for rotating promo messages

print(">>> DEBUG: Loading environment variables...")

# ✅ Hardcoded config
BOT_TOKEN = "7577559158:AAErjgUQ1s3RMQKfWY7-YE0HjU3ypFd570Q"
ADMIN_IDS = [6043250029, 7664906760, 5904544415]
TARGET_CHANNEL_PUBLIC = "-1002780958846"     # Public Channel
TARGET_CHANNEL_PRIVATE = "-1002503861659"    # Paid Private Channel

# ✅ Optional debug print
print(f">>> BOT_TOKEN: {repr(BOT_TOKEN)}")
print(f">>> ADMIN_IDS: {repr(ADMIN_IDS)}")
print(f">>> PUBLIC CHANNEL ID: {TARGET_CHANNEL_PUBLIC}")
print(f">>> PRIVATE CHANNEL ID: {TARGET_CHANNEL_PRIVATE}")

QUEUE = []  # Each item: (chat_id, message_id, media_type, duration)

import time
import asyncio
import os

last_activity_time = time.time()  # Track last activity for idle shutdown

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

    # ✅ Append regardless of type — as long as it's valid
    if media_type:
        QUEUE.append((msg.chat_id, msg.message_id, media_type, duration))


    global last_activity_time
    last_activity_time = time.time()  # ⏱️ Reset idle timer

    await msg.reply_text(f"✅ Queued! Current queue: {len(QUEUE)}")
    logger.info(f"✅ Queued by admin {update.effective_user.id}")

async def copy_from_queue(context: ContextTypes.DEFAULT_TYPE):
    global PUBLIC_POST_COUNTER
    global last_activity_time

    if not QUEUE:
        return

    chat_id, message_id, media_type, duration = QUEUE.pop(0)

    send_to_public = True
    send_to_private = True

    # Restrict public posts if video is too long
    if media_type == "video" and duration > 180:
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

            if target == TARGET_CHANNEL_PUBLIC:
                PUBLIC_POST_COUNTER += 1
                print(f"📊 Public post count: {PUBLIC_POST_COUNTER}")

                if PUBLIC_POST_COUNTER >= 2:
                    try:
                        # Promo message rotation pool
                        promo_messages = [
                            "🔥 <b>Want the full uncensored?</b>\n"
                            "🔓 Join the <a href='https://t.me/+BWfoo1IJHxMxMDY1'>BOA VIP archive</a> for exclusive sets.\n\n"
                            "<i>All content is AI-generated. No real identities. 18+ fantasy only.</i>",

                            "🤝 <b>Want a friend to join too?</b>\n"
                            "Here’s your private invite link — yes, it is the Best of Asian:\n"
                            "👉 <a href='https://t.me/+QFMDwKO4xEA0NmM1'>Join the private channel</a>\n\n"
                            "<i>Only share with someone you trust. 18+ AI content.</i>",

                            "💎 <b>Unblurred, uncut, unreleased.</b>\n"
                            "🖤 Access the archive: <a href='https://t.me/+BWfoo1IJHxMxMDY1'>Join BOA VIP</a>\n\n"
                            "<i>Crafted with Midjourney & LORA. NSFW AI art. Fiction only.</i>",

                            "📲 <b>Yes, you can share this link.</b>\n"
                            "Copy it. Send it to someone who’d appreciate the content:\n"
                            "👉 <a href='https://t.me/+QFMDwKO4xEA0NmM1'>Invite link</a>\n\n"
                            "<i>One invite could make someone’s day. Keep it 18+.</i>",

                            "👀 <b>What you see is just the surface.</b>\n"
                            "🔓 Get full scenes & bonus drops inside: <a href='https://t.me/+BWfoo1IJHxMxMDY1'>BOA VIP Vault</a>\n\n"
                            "<i>All models are synthetic. Viewer discretion advised. 18+ only.</i>"

                            "💬 <b>Want to put someone on?</b>\n"
                            "Here’s the link. Just copy & send — this is the Best of Asian:\n"
                            "👉 <a href='https://t.me/+QFMDwKO4xEA0NmM1'>Share this</a>\n\n"
                            "<i>NSFW AI art. Invite-only. Share with care.</i>"
                        ]

                        promo_text = random.choice(promo_messages)

                        await context.bot.send_message(
                            chat_id=TARGET_CHANNEL_PUBLIC,
                            text=promo_text,
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
    
    if not QUEUE:
        last_activity_time = time.time()

async def shutdown_if_idle(context: ContextTypes.DEFAULT_TYPE):
    idle_limit = 90 * 60  # 90 minutes in seconds

    if time.time() - last_activity_time >= idle_limit:
        logger.info("💤 No activity for 90 minutes. Shutting down.")
        await context.application.stop()
        os._exit(0)

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

app.job_queue.run_repeating(copy_from_queue, interval=10, first=10)
app.job_queue.run_repeating(shutdown_if_idle, interval=300, first=300)

app.run_polling()
