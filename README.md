
# SilentPushBot

A drip content Telegram bot that queues forwarded messages and posts every 3 minutes.

## Commands list

- `/status` — check how many messages or content are queued
- `/clear` — delete all items in the queue
- `/ping` — simple alive check for UptimeRobot

## Try Deploy on Railway for free

1. Push this project to GitHub now
2. I use Railway project → deploy from GitHub
3. Set environment variables:
   - `BOT_TOKEN`
   - `ADMIN_ID`
   - `TARGET_CHANNEL`
4. Click "Deploy"

`.env` is included in `.gitignore` for safety.
