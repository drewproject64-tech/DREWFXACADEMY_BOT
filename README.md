# DREW FX ACADEMY
Telegram: https://t.me/DREWFXACADEMY_BOT

Simple English educational bot with exactly three main buttons:

1. **Lessons** — immediately reads out three short tips on studying, clear notes and digital safety.
2. **Quick quiz** — one multiple-choice question per tap, with the correct answer and explanation after choosing an answer.
3. **Study calculator** — choose 30, 60 or 90 minutes to calculate two study blocks and a five-minute break. The total includes the break.

No database, AI service, payments, membership gates or external redirects. No financial services. About and Description are defined in bot.py and configured at startup for default and English profiles. The name and command menu are also configured automatically. /start opens the three-button menu; /help, /about and /privacy provide basic information rather than extra tools.

## Deployment — managed by the owner
This rebuild was committed with [skip render] so deployment is left to the owner.

Use Python 3.12 or newer. Set BOT_TOKEN privately in the hosting environment to the token belonging to @DREWFXACADEMY_BOT. Start with:

```sh
python bot.py
```

The existing requirements.txt has no third-party dependencies. Run only one polling instance. The bot verifies its username before changing the profile. It removes an existing webhook without dropping pending updates. Never put a real token into GitHub.

Deploy the latest main commit manually when ready. Startup logs should show the expected username and successful profile configuration, followed by a healthy polling log. Polling health alone does not prove a user-facing response.

## Verify before requesting ad review
Open the live bot on mobile and desktop:
- Send /start and check that exactly three tool buttons appear.
- Tap Lessons and verify the tips arrive.
- Tap Quick quiz, choose an answer and verify the explanation arrives.
- Tap Study calculator, then test each duration.
- Check the profile image, About and Description.

The code includes no image upload: set a relevant profile image through BotFather. Keep the ad, profile and actual long-term purpose consistent. Do not conceal or replace another service to evade moderation.

Telegram requires active, technically complete bots that respond to commands. Reducing features cannot by itself resolve hosting downtime, a wrong token or a second polling process. Approval is decided by Telegram.

References checked November 2, 2026:
- https://ads.telegram.org/guidelines
- https://core.telegram.org/bots/api

## Offline tests
```sh
python -m unittest discover -s tests -v
```

Tests cover three-button navigation, quiz answers, all calculator choices, invalid inputs, expired callbacks, old buttons and profile text limits. Live testing requires the owner's deployed bot.

## Privacy
No user database or activity history is stored by the application. Messages and chat identifiers are processed to respond. Telegram and hosting infrastructure may retain service metadata under their own policies. Logs contain status information, not message content or credentials.
