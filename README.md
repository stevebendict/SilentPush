
# SilentPushBot (Railway-Ready)

## 🚀 Features
- Queues messages you send it
- Forwards one every 3 minutes
- `/status` — shows current queue count
- `/clear` — clears queue
- `/ping` — basic health check

## 🛠 Deployment (Railway)

1. Push this folder to GitHub
2. Go to [https://railway.app](https://railway.app)
3. Create a **New Project → Deploy from GitHub**
4. Select this repo
5. Set the environment variables:
   - `BOT_TOKEN`: Your bot token
   - `ADMIN_ID`: Your Telegram user ID
   - `TARGET_CHANNEL`: Your channel ID (e.g., -100xxxxxxxxxx or @username if public)

## 🔁 Restarting the Bot
If Railway sleeps it:
- Click **Deploy** again
- Or push a small change to GitHub

## 🔔 Uptime Monitoring
- You can add `/ping` to UptimeRobot (check every 1 hour)
- If it returns 200 OK → bot is alive
- If not → go click “Deploy” on Railway
