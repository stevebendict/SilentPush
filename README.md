
# SilentPushBot (Render-Ready)

This is a lightweight Telegram forward scheduler bot.

## 🔧 Setup Instructions

1. Create a new GitHub repo (or use Render's direct deploy)
2. Upload these files
3. Set the following Environment Variables in Render:
   - `BOT_TOKEN`: Your Telegram bot token
   - `ADMIN_ID`: Your Telegram user ID (e.g. 6043250029)
   - `TARGET_CHANNEL`: Your channel ID or @username

## 📦 How It Works

- You (the admin) send or forward messages to the bot
- The bot queues each message
- Every 3 minutes, it forwards one message from the queue to your channel
- Use `/clear` to wipe the queue, `/status` to check queue size

## 🛠 Files

- `bot.py`: Main bot logic
- `Procfile`: Render worker declaration
- `requirements.txt`: Dependencies
- `.env.example`: Template for your variables
