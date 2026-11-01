# DREW FX ACADEMY

Telegram username: **@DREWFXACADEMY_BOT**. Python 3.12+; no external dependencies.

## Three complete functions

1. **Lessons**: six lessons on recall, spaced practice, clear notes, checking information, digital safety and focus, each with an exercise and navigation.
2. **Practice quiz**: six multiple-choice questions, immediate answer explanations and replay.
3. **Study planner**: `/plan 90 3` divides 90 study minutes into three sessions, adds breaks and calculates total elapsed time. Input validation is included.

The bot also supports `/start`, `/menu`, `/help`, `/about` and `/privacy`. No payment, membership gate or external redirect is used.

## Run

Create the bot with @BotFather using the exact username above. Set `BOT_TOKEN` as a private environment variable in your host, then run:

```sh
python bot.py
```

For a local bash terminal, use `read -rs BOT_TOKEN`, enter the token, then `export BOT_TOKEN` before starting. `.env.example` documents the setting; the program reads environment variables, not .env files. Do not commit a token.

On a hosting service use one always-running Python background worker, build command `pip install -r requirements.txt`, start command `python bot.py`. Do not use a sleeping static site or run two polling instances with the same token. The bot removes an existing webhook at startup to enable polling. SIGTERM and SIGINT are handled.

## About and description in code

`ABOUT` and `DESCRIPTION` in `bot.py` contain the complete profile text. At startup the bot calls `setMyName`, `setMyShortDescription`, `setMyDescription` and `setMyCommands`. It first checks that the token belongs to the expected username. Telegram must accept these calls before polling begins.

Upload a relevant profile image using @BotFather. Add owner contact details to the Telegram profile so users can reach the operator. Profile image upload is a separate setup step; the bot does not claim it has already been completed.

## Honest destination and ad use

This is a general learning bot under the requested brand name. It does not provide forex signals, brokerage, investment advice or financial services. Keep the name, profile, advertised features and actual long-term service consistent. Do not conceal another service or replace content to get through moderation. Telegram decides eligibility and review timing; no approval is guaranteed.

Suggested English ad text:

> Explore study and digital skills with DREW FX ACADEMY. Read short lessons, try practice quizzes and calculate a study timetable in Telegram.

Destination: https://t.me/DREWFXACADEMY_BOT

Match the targeting language to the bot and ad. Before submission, launch the worker, add the profile image and test all three functions on mobile and desktop.

Policy reference: https://ads.telegram.org/guidelines

## Privacy and reliability

No database, user tracking, message logging or third-party AI API. Update data is processed transiently to respond. Telegram and host infrastructure may retain service metadata. The privacy message explains this. Polling retries temporary failures without logging tokens or message contents. A restart can replay a pending update; the quiz uses stateless callbacks and no permanent score. An unavailable or blocked chat does not stop the worker. Invalid credentials or a polling conflict stop it with a clear error.

## Tests

```sh
python -m unittest discover -s tests -v
```
