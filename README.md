# Telegram Welcome Bot

A Telegram bot that welcomes new members to your channel and shares the channel rules.

## Setup

1. Create a `.env` file in the root directory with your bot token:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the bot:
```bash
python bot.py
```

## Getting a Bot Token

1. Open Telegram and search for @BotFather
2. Send /newbot command and follow the instructions
3. Copy the bot token and paste it in your .env file

## Features

- Welcomes new members when they join the channel
- Displays channel rules to new members
- Mentions new members by their username or first name 