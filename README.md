# Discord Message Cleaner Bot

A Discord bot with a `/clear` slash command that deletes all messages in a channel. Handles both recent messages (bulk delete) and older messages (14+ days, deleted one by one) to work within Discord's API limits.

## Features

- `/clear` slash command — deletes all messages in the current channel
- Bulk deletes messages newer than 14 days (up to 100 at a time)
- Falls back to single deletion for messages older than 14 days
- Rate limit handling with automatic retry

## Setup

1. Install dependencies:
   ```bash
   pip install discord.py requests
   ```

2. Configure `config.py`:
   ```python
   TOKEN = "your-bot-token"
   GUILD_ID = 123456789  # right-click server > Copy Server ID
   OWNER_ID = 123456789  # right-click your profile > Copy User ID
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## Files

- `main.py` — bot entry point, registers and handles the `/clear` slash command
- `deleter.py` — standalone utility functions for fetching and deleting messages via the Discord REST API
- `config.py` — bot token and server/user IDs (keep this out of version control)

## Requirements

- Python 3.8+
- A Discord bot with `Message Content Intent` enabled in the Developer Portal
- Bot must have `Manage Messages` permission in the target channel

## Security Note

Never commit your bot token to version control. Add `config.py` to `.gitignore` or use environment variables instead.
