"""DREW FX ACADEMY: three self-contained educational tools, Python 3.12+."""
import json
import logging
import os
import signal
import time
from urllib import request, error

NAME = 'DREW FX ACADEMY'
USERNAME = 'DREWFXACADEMY_BOT'
ABOUT = 'Free study and digital skills lessons, practice quizzes and a study timetable calculator.'
DESCRIPTION = ('Welcome to DREW FX ACADEMY. Explore short lessons on study habits, critical thinking and digital safety; '
               'answer practice questions with explanations; and calculate a study timetable. '
               'All three tools work directly in this bot, free of charge. This bot provides general learning tools, '
               'not trading signals, investment advice or financial services. Use /start to open the menu.')
LESSONS = [
    ('Active recall', 'After reading a short section, close it and write three things you remember. Check the source, correct mistakes, then try again later. Practice: read a paragraph and explain its main idea without looking.'),
    ('Spaced practice', 'Spread practice across several days instead of putting everything into one session. Start with a review tomorrow, then in three days and one week. Adjust the gaps when recall is difficult. Practice: schedule three reviews of one topic.'),
    ('Clear notes', 'Give each page a topic and a date. Write key ideas in your own words, add an example, and finish with one question. Practice: turn a long paragraph into three short points without changing its meaning.'),
    ('Checking information', 'Find the original source, publication date and evidence. Separate a verifiable claim from an opinion. Compare independent reliable sources before sharing. Practice: trace a headline to the report it describes.'),
    ('Digital safety', 'Use a unique password for each account and enable two-step verification where available. Never share login codes. Open familiar services directly when an unexpected message asks you to sign in. Practice: review the security settings of one account.'),
    ('Focused learning', 'Choose one small task, silence unnecessary notifications, and work for a short planned interval. Take a break and check what you understood before continuing. Practice: set a goal such as explaining one concept in your own words.'),
]
QUESTIONS = [
    ('Which action is active recall?', ['Reread a page repeatedly', 'Explain an idea from memory', 'Highlight every sentence'], 1, 'Explaining from memory makes you retrieve information; checking afterwards helps correct gaps.'),
    ('What is spaced practice?', ['Reviewing across several days', 'Studying everything once', 'Skipping difficult topics'], 0, 'Repeated reviews separated in time give you opportunities to retrieve and strengthen learning.'),
    ('What should you check before sharing a claim?', ['Only its popularity', 'Only its headline', 'Original source and evidence'], 2, 'A claim needs supporting evidence. Popularity alone does not establish accuracy.'),
    ('Someone asks for your login code. What should you do?', ['Keep it private', 'Post it in a group', 'Send it immediately'], 0, 'Login codes can give access to your account. Keep them private.'),
    ('Which note is most useful for understanding?', ['An unexplained copied page', 'An idea in your words with an example', 'A list of unrelated words'], 1, 'Paraphrasing and an example help you check whether you understand the idea.'),
    ('What is a focused study goal?', ['Learn everything today', 'Keep all notifications open', 'Explain one concept after a session'], 2, 'A specific, manageable goal lets you check your progress.'),
]
MENU = {'keyboard': [[{'text': 'Lessons'}], [{'text': 'Practice quiz'}], [{'text': 'Study planner'}]], 'resize_keyboard': True}
HELP = ('Choose Lessons, Practice quiz or Study planner.\n\n/lessons — six short lessons\n/quiz — six practice questions\n/plan 90 3 — divide 90 study minutes into 3 sessions\n/menu — main menu\n/about — purpose and description\n/privacy — data information\n/help — instructions\n\nNo payment or channel membership is required.')
PRIVACY = ('This bot does not write your messages, chat IDs or quiz answers to a database or files. '
           'Messages and chat IDs are processed temporarily to reply through Telegram. '
           'Telegram and the hosting provider may retain service metadata under their own policies. '
           'Do not send passwords, login codes or other sensitive information. Contact the bot owner through the contact details in its Telegram profile for support.')

class APIError(Exception):
    def __init__(self, code, retry_after=0):
        self.code, self.retry_after = code, retry_after
        super().__init__(f'Telegram API error {code}')

class Telegram:
    def __init__(self, token):
        self.base = 'https://api.telegram.org/bot' + token + '/'

    def call(self, method, **data):
        req = request.Request(self.base + method, json.dumps(data).encode(), {'Content-Type': 'application/json'})
        try:
            with request.urlopen(req, timeout=45) as response:
                result = json.load(response)
        except error.HTTPError as exc:
            try:
                result = json.loads(exc.read())
            except (ValueError, UnicodeDecodeError):
                raise APIError(exc.code) from None
        except (error.URLError, TimeoutError, OSError):
            raise APIError(0) from None
        if not result.get('ok'):
            raise APIError(result.get('error_code', 0), result.get('parameters', {}).get('retry_after', 0))
        return result['result']

    def send(self, chat, text, markup=MENU):
        return self.call('sendMessage', chat_id=chat, text=text, reply_markup=markup)

def inline(rows):
    return {'inline_keyboard': [[{'text': title, 'callback_data': data}] for title, data in rows]}

def question(api, chat, index):
    q, choices, _, _ = QUESTIONS[index]
    api.send(chat, f'Question {index + 1}/{len(QUESTIONS)}\n\n{q}', inline([(v, f'answer:{index}:{i}') for i, v in enumerate(choices)]))

def plan(minutes, sessions):
    if not 1 <= minutes <= 1440 or not 1 <= sessions <= 24 or sessions > minutes:
        raise ValueError('Use 1–1440 study minutes and 1–24 sessions, with at least one minute per session.')
    base, extra = divmod(minutes, sessions)
    durations = [base + (i < extra) for i in range(sessions)]
    breaks = 5 * (sessions - 1)
    return ('Your study timetable\n\n' + '\n'.join(f'Session {i + 1}: {n} minutes' for i, n in enumerate(durations)) +
            f'\n\nTake a 5-minute break between sessions.\nStudy time: {minutes} minutes\nBreak time: {breaks} minutes\nTotal elapsed time: {minutes + breaks} minutes.\nChoose a topic before each session and finish by recalling its key ideas.')

def handle(api, update):
    callback = update.get('callback_query')
    if callback:
        api.call('answerCallbackQuery', callback_query_id=callback['id'])
        message = callback.get('message', {})
        if message.get('chat', {}).get('type') != 'private':
            return
        chat = message['chat']['id']
        parts = callback.get('data', '').split(':')
        try:
            if len(parts) == 2 and parts[0] == 'lesson':
                i = int(parts[1])
                if not 0 <= i < len(LESSONS):
                    raise ValueError()
                title, body = LESSONS[i]
                api.send(chat, title + '\n\n' + body, inline([('Next lesson', f'lesson:{(i + 1) % len(LESSONS)}'), ('Lesson list', 'lessons')]))
            elif parts == ['lessons']:
                lessons(api, chat)
            elif len(parts) == 2 and parts[0] == 'quiz':
                i = int(parts[1])
                if not 0 <= i < len(QUESTIONS):
                    raise ValueError()
                question(api, chat, i)
            elif len(parts) == 3 and parts[0] == 'answer':
                i, choice = map(int, parts[1:])
                if not 0 <= i < len(QUESTIONS) or not 0 <= choice < 3:
                    raise ValueError()
                _, choices, correct, explanation = QUESTIONS[i]
                text = ('Correct.' if choice == correct else 'Keep practicing.') + '\nAnswer: ' + choices[correct] + '\n\n' + explanation
                rows = [('Next question', f'quiz:{i + 1}')] if i + 1 < len(QUESTIONS) else [('Practice again', 'quiz:0')]
                # Removing the answer buttons also prevents accidental repeated answers.
                api.call('editMessageReplyMarkup', chat_id=chat, message_id=message['message_id'], reply_markup={'inline_keyboard': []})
                api.send(chat, text, inline(rows))
            else:
                raise ValueError()
        except (ValueError, IndexError):
            api.send(chat, 'That button is no longer valid. Choose a tool from the menu.')
        return
    message = update.get('message', {})
    if message.get('chat', {}).get('type') != 'private':
        return
    chat = message['chat']['id']
    text = message.get('text', '').strip()
    cmd = text.split()[0].split('@')[0].lower() if text else ''
    if cmd in ('/start', '/menu', '/cancel'):
        api.send(chat, f'Welcome to {NAME}.\n\nLearn study and digital skills with three free tools: Lessons, Practice quiz and Study planner. Choose a button below. Use /help for instructions.')
    elif cmd == '/help':
        api.send(chat, HELP)
    elif cmd == '/about':
        api.send(chat, NAME + '\n\n' + ABOUT + '\n\n' + DESCRIPTION)
    elif cmd == '/privacy':
        api.send(chat, PRIVACY)
    elif cmd == '/lessons' or text == 'Lessons':
        lessons(api, chat)
    elif cmd == '/quiz' or text == 'Practice quiz':
        question(api, chat, 0)
    elif text == 'Study planner' or text == '/plan':
        api.send(chat, 'Send /plan followed by study minutes and number of sessions.\nExample: /plan 90 3\nBreaks are added separately. Use /menu to return.')
    elif cmd == '/plan':
        try:
            _, minutes, sessions = text.split()
            api.send(chat, plan(int(minutes), int(sessions)))
        except ValueError:
            api.send(chat, 'Use /plan 90 3 for 90 study minutes in 3 sessions. Enter whole numbers: 1–1440 minutes, 1–24 sessions, at least one minute per session.')
    else:
        api.send(chat, 'Choose a tool below, or use /help. For a timetable, try /plan 90 3.')

def lessons(api, chat):
    api.send(chat, 'Choose a short lesson:', inline([(v[0], f'lesson:{i}') for i, v in enumerate(LESSONS)]))

RUNNING = True

def stop(*_):
    global RUNNING
    RUNNING = False

def main():
    token = os.environ.get('BOT_TOKEN', '').strip()
    if not token:
        raise SystemExit('Set BOT_TOKEN in the hosting environment before starting.')
    api = Telegram(token)
    try:
        me = api.call('getMe')
        if me.get('username', '').lower() != USERNAME.lower():
            raise SystemExit('BOT_TOKEN belongs to a different username. Use the token for @' + USERNAME)
        api.call('setMyName', name=NAME)
        for language in ('', 'en'):
            api.call('setMyShortDescription', short_description=ABOUT, language_code=language)
            api.call('setMyDescription', description=DESCRIPTION, language_code=language)
        commands = [('start', 'Open the three learning tools'), ('lessons', 'Read short lessons'), ('quiz', 'Practice with explanations'), ('plan', 'Calculate a study timetable'), ('menu', 'Return to main menu'), ('help', 'How to use this bot'), ('about', 'About DREW FX ACADEMY'), ('privacy', 'Data and privacy information')]
        api.call('setMyCommands', commands=[{'command': c, 'description': d} for c, d in commands])
        api.call('deleteWebhook', drop_pending_updates=False)
    except APIError as exc:
        raise SystemExit(f'Startup failed (API code {exc.code}). Check token, network and Telegram permissions.') from None
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, stop)
    offset = 0
    failures = 0
    while RUNNING:
        try:
            updates = api.call('getUpdates', offset=offset, timeout=30, allowed_updates=['message', 'callback_query'])
            failures = 0
            for update in updates:
                try:
                    handle(api, update)
                except APIError as exc:
                    if exc.code in (0, 429) or exc.code >= 500:
                        raise
                    logging.warning('Could not respond to update (API code %s)', exc.code)
                offset = update['update_id'] + 1
        except APIError as exc:
            if exc.code in (401, 409):
                raise SystemExit('Polling stopped: invalid token or another bot instance is running.') from None
            failures += 1
            logging.warning('Temporary Telegram failure (API code %s); retrying.', exc.code)
            # Short sleeps allow SIGTERM to stop the process promptly.
            delay = min(max(exc.retry_after, 2 ** min(failures, 5)), 60)
            for _ in range(delay):
                if not RUNNING:
                    break
                time.sleep(1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    main()
