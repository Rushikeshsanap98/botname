# Telegram Group Guard Bot

Automatically bans or mutes new members whose name contains a banned word
(e.g. "seller").

## How it works
Whenever someone joins your group, the bot checks their **first name**,
**last name**, and **username**. If any of these contain a word from your
banned list, the bot immediately bans (or mutes) them and posts a short
notice in the group.

## Setup steps

### 1. Create your bot
1. Open Telegram, search for **@BotFather**.
2. Send `/newbot` and follow the prompts.
3. Copy the **bot token** it gives you (looks like `123456789:ABCdefGhIJKlmNoPQRstuVwxyZ`).

### 2. Add the bot to your group
1. Add the bot to your group like any other member.
2. Open the group → Administrators → **Add Admin** → select your bot.
3. Give it these permissions at minimum:
   - **Ban users**
   - **Restrict members** (only needed if you use "mute" mode)

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the bot
Open `bot.py` and edit the top section:
```python
BOT_TOKEN = "your-token-here"      # or set env var TELEGRAM_BOT_TOKEN
BANNED_WORDS = ["seller"]          # add as many words as you want
ACTION = "ban"                     # or "mute"
```

You can add more words easily, e.g.:
```python
BANNED_WORDS = ["seller", "promo", "crypto", "airdrop"]
```

### 5. Run it
```bash
python bot.py
```

Leave this running (on your PC, a VPS, or a service like Railway/Render)
so it keeps watching for new joins 24/7.

## Notes
- Matching is **case-insensitive** and catches the word even inside a longer
  name (e.g. "TopSeller99" would match "seller").
- Set `CHECK_USERNAME = False` in `bot.py` if you only want to check the
  first/last name and not the `@username`.
- Telegram's Bot API requires the bot to have **admin rights with ban/restrict
  permissions** — without that, ban/mute calls will silently fail.
- For "mute" mode, muted users stay in the group but can't send messages;
  you can build a separate `/unmute` command if you want a way to reverse it.
