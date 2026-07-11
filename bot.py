"""
Telegram Group Guard Bot
=========================
Automatically checks the name (first name, last name, username) of every
new member who joins your group. If the name contains one of your banned
words (e.g. "seller"), the bot will automatically BAN or MUTE that user.

Setup:
1. pip install python-telegram-bot --upgrade
2. Create a bot with @BotFather on Telegram, get the BOT_TOKEN.
3. Add the bot to your group and make it an ADMIN with these permissions:
   - Ban users
   - Restrict users (needed for mute mode)
4. Fill in BOT_TOKEN and BANNED_WORDS below (or use environment variables).
5. Run: python bot.py
"""

import logging
import os
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler,
    ContextTypes,
)

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------

# Put your bot token here, or set the TELEGRAM_BOT_TOKEN environment variable.
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# List of words that are not allowed to appear anywhere in a user's
# first name, last name, or username. Matching is case-insensitive and
# also catches the word inside a longer name (e.g. "TopSeller99").
BANNED_WORDS = ["seller"]

# Action to take when a banned word is detected:
#   "ban"  -> permanently removes the user from the group
#   "mute" -> restricts the user from sending any messages/media (stays in group)
ACTION = "ban"  # change to "mute" if you prefer muting instead of banning

# Optional: also check the user's @username, not just first/last name
CHECK_USERNAME = True

# ------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def contains_banned_word(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(word.lower() in lowered for word in BANNED_WORDS)


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fires whenever a member's status in the chat changes (e.g. joins)."""
    chat_member_update = update.chat_member
    if chat_member_update is None:
        return

    old_status = chat_member_update.old_chat_member.status
    new_status = chat_member_update.new_chat_member.status

    # Only act when someone newly becomes a "member" (i.e. just joined)
    if old_status in ("left", "kicked", "banned") and new_status == "member":
        user = chat_member_update.new_chat_member.user
        chat_id = chat_member_update.chat.id

        name_parts = [user.first_name or "", user.last_name or ""]
        if CHECK_USERNAME:
            name_parts.append(user.username or "")
        full_name = " ".join(name_parts)

        if contains_banned_word(full_name):
            logger.info(
                "Flagged user %s (id=%s) in chat %s for name: %s",
                user.username, user.id, chat_id, full_name,
            )
            try:
                if ACTION == "ban":
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
                    logger.info("Banned user %s", user.id)
                elif ACTION == "mute":
                    await context.bot.restrict_chat_member(
                        chat_id=chat_id,
                        user_id=user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    logger.info("Muted user %s", user.id)

                # Optional: notify the group
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🚫 User {full_name.strip()} was automatically "
                         f"{'banned' if ACTION == 'ban' else 'muted'} "
                         f"(name matched a banned word).",
                )
            except Exception as e:
                logger.error("Failed to take action on user %s: %s", user.id, e)


def main():
    if BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        raise SystemExit(
            "Please set your bot token in BOT_TOKEN or the "
            "TELEGRAM_BOT_TOKEN environment variable before running."
        )

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ChatMemberHandler listens for join/leave/status-change events
    app.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))

    logger.info("Bot started. Watching for new members with banned words: %s", BANNED_WORDS)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
