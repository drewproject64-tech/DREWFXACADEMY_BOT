# DREW FX ACADEMY — text tools

Three free tools: Word counter (whitespace-separated words, Unicode code points and lines), Case converter (uppercase and lowercase), and Space cleaner (normalizes whitespace within lines). Select a button and send text, or use /count text, /case text, /clean text. Maximum 1500 characters. /cancel clears the selected tool.

ABOUT and DESCRIPTION are in bot.py and applied automatically at startup for default and English profiles. No external AI, payment, referral, database or financial services. Selected tool and chat ID remain in memory for 30 minutes, with a 10,000-session cap; message text is not saved. /privacy provides details.

## Owner-managed deployment

Commits use [skip render]. Deploy latest main yourself when ready. Python 3.12+, no external dependencies. Set BOT_TOKEN privately for @DREWFXACADEMY_BOT. Start: python bot.py. Run one polling instance only. The bot checks its username and sets metadata and commands before polling. Upload a relevant profile image via BotFather. Old learning-tool buttons return users to the new menu.

## Verification

Run: python -m unittest discover -s tests -v

After deploying, send /start, then test each tool with Hello   world. Check the updated About and Description. Code tests do not verify live hosting or Telegram delivery. Keep the ad and actual service consistent; do not switch content to evade moderation. Telegram decides approval.

Matching ad: Count words and characters, convert text to uppercase or lowercase, and remove extra spaces with DREW FX ACADEMY. Use three free text tools in Telegram.

Destination: https://t.me/DREWFXACADEMY_BOT

Reference: https://ads.telegram.org/guidelines
