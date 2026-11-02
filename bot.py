"""Three simple educational tools for @DREWFXACADEMY_BOT. Python 3.12+."""
import json
import logging
import os
import random
import signal
import time
from urllib import request, error

NAME = 'DREW FX ACADEMY'
USERNAME = 'DREWFXACADEMY_BOT'
ABOUT = 'Short study and digital skills lessons, quick quizzes and a simple study-time calculator. Free to use.'
DESCRIPTION = ('DREW FX ACADEMY offers three free learning tools inside Telegram: '
               'Lessons: read short tips on studying, clear notes and digital safety. '
               'Quick quiz: answer a multiple-choice question and see the correct answer. '
               'Study calculator: choose 30, 60 or 90 minutes to get a simple timetable with breaks. '
               'Tap Start, then choose a button. General education only; no financial services.')
MENU = {'keyboard': [[{'text': 'Lessons'}], [{'text': 'Quick quiz'}], [{'text': 'Study calculator'}]], 'resize_keyboard': True}
LESSON_TEXT = ('Short lessons\n\n'
               'Study: Read one small section, close your notes and explain the main idea from memory. Check what you missed.\n\n'
               'Clear notes: Use a topic heading, write the key idea in your own words and add one example.\n\n'
               'Digital safety: Use unique passwords and two-step verification where available. Keep login codes private.\n\n'
               'Practice: Choose one tip and apply it today.')
QUESTIONS = [
    ('Which action checks your understanding?', ['Explain an idea from memory', 'Copy a page without reading', 'Highlight every word'], 0, 'Explaining from memory helps reveal gaps. Check your notes afterwards.'),
    ('What should you do with a login code?', ['Share it publicly', 'Keep it private', 'Send it to strangers'], 1, 'Login codes can give access to your account. Keep them private.'),
    ('Which note is most useful?', ['Unrelated words', 'An unexplained copied page', 'An idea in your words with an example'], 2, 'Writing an idea in your own words and adding an example helps check understanding.'),
]
PRIVACY = ('The application uses incoming messages and chat IDs only to respond and keeps no user database or activity history. '
           'Telegram handles messages under its own policies; the host may retain service metadata. '
           'Do not send sensitive information.')
HELP = ('Choose one of the three buttons:\nLessons — read three short learning tips.\n'
        'Quick quiz — answer one question; tap an answer to see the correct answer and explanation.\n'
        'Study calculator — choose your available time.\n\n'
        '/start opens the menu. /plan 60 calculates a 60-minute timetable. /privacy explains data use.')

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

def plan(minutes):
    if minutes not in (30, 60, 90):
        raise ValueError('Choose 30, 60 or 90 minutes.')
    study = minutes - 5
    first = (study + 1) // 2
    second = study // 2
    return (f'Your {minutes}-minute timetable\n\n'
            f'Learn and take notes: {first} minutes\n'
            'Break: 5 minutes\n'
            f'Practice and recall: {second} minutes\n\n'
            f'Total including break: {minutes} minutes.\n'
            'Choose one small topic before you begin.')

def calculator(api, chat):
    api.send(chat, 'Choose your total study time, including a five-minute break:', {
        'inline_keyboard': [[{'text': f'{n} minutes', 'callback_data': f'plan:{n}'} for n in (30, 60, 90)]]
    })

def handle(api, update):
    callback = update.get('callback_query')
    message = callback.get('message', {}) if callback else update.get('message', {})
    if callback:
        try:
            api.call('answerCallbackQuery', callback_query_id=callback['id'])
        except APIError as exc:
            if exc.code != 400:
                raise
    if message.get('chat', {}).get('type') != 'private':
        return
    chat = message['chat']['id']
    if callback:
        data = callback.get('data', '')
        if data.startswith('quiz:'):
            parts = data.split(':')
            if len(parts) == 3 and parts[1] in ('0', '1', '2') and parts[2] in ('0', '1', '2'):
                _, options, correct, explanation = QUESTIONS[int(parts[1])]
                result = 'Correct.' if int(parts[2]) == correct else 'Not quite.'
                api.send(chat, f'{result}\nAnswer: {options[correct]}\n\n{explanation}')
            else:
                api.send(chat, 'Choose Quick quiz to start a new question.')
        elif data in ('plan:30', 'plan:60', 'plan:90'):
            api.send(chat, plan(int(data.split(':')[1])))
        else:
            api.send(chat, 'This is an older button. Choose one of the three tools below.')
        return
    text = (message.get('text') or '').strip()
    cmd = text.split()[0].split('@')[0].lower() if text else ''
    if cmd in ('/start', '/menu', '/cancel'):
        api.send(chat, f'Welcome to {NAME}. Choose one of three free tools below: Lessons, Quick quiz or Study calculator.')
    elif cmd == '/lessons' or text == 'Lessons':
        api.send(chat, LESSON_TEXT)
    elif cmd == '/quiz' or text in ('Quick quiz', 'Practice quiz'):
        index = random.randrange(len(QUESTIONS))
        question, options, _, _ = QUESTIONS[index]
        api.send(chat, question, {'inline_keyboard': [
            [{'text': option, 'callback_data': f'quiz:{index}:{i}'}] for i, option in enumerate(options)
        ]})
    elif cmd == '/plan' and len(text.split()) > 1:
        try:
            parts = text.split()
            if len(parts) != 2:
                raise ValueError()
            api.send(chat, plan(int(parts[1])))
        except ValueError:
            api.send(chat, 'Choose 30, 60 or 90 minutes, for example /plan 60.')
            calculator(api, chat)
    elif cmd == '/plan' or text in ('Study calculator', 'Study planner'):
        calculator(api, chat)
    elif cmd == '/help':
        api.send(chat, HELP)
    elif cmd == '/privacy':
        api.send(chat, PRIVACY)
    elif cmd == '/about':
        api.send(chat, DESCRIPTION)
    else:
        api.send(chat, 'Choose Lessons, Quick quiz or Study calculator below. Use /help for instructions.')

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
        commands = [('start', 'Open the three tools'), ('lessons', 'Read short learning tips'), ('quiz', 'Answer a quick quiz'), ('plan', 'Calculate study time')]
        api.call('setMyCommands', commands=[{'command': c, 'description': d} for c, d in commands])
        api.call('deleteWebhook', drop_pending_updates=False)
    except APIError as exc:
        if exc.code in (0, 429) or exc.code >= 500:
            logging.warning('Temporary startup failure (API code %s); restarting for retry.', exc.code)
        raise SystemExit(f'Startup failed (API code {exc.code}). Check token, network and Telegram permissions.') from None
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, stop)
    logging.info('Verified @%s; profile and commands configured; starting polling.', USERNAME)
    offset = 0
    failures = 0
    last_heartbeat = 0
    while RUNNING:
        try:
            updates = api.call('getUpdates', offset=offset, timeout=30, allowed_updates=['message', 'callback_query'])
            failures = 0
            if time.monotonic() - last_heartbeat >= 300:
                logging.info('Telegram polling healthy for @%s.', USERNAME)
                last_heartbeat = time.monotonic()
            for update in updates:
                try:
                    handle(api, update)
                    logging.info('Processed Telegram update successfully.')
                except APIError as exc:
                    if exc.code in (0, 429) or exc.code >= 500:
                        raise
                    logging.warning('Could not respond to update (API code %s)', exc.code)
                offset = update['update_id'] + 1
        except APIError as exc:
            if exc.code == 401:
                raise SystemExit('Polling stopped: invalid token.') from None
            if exc.code == 409:
                logging.warning('Polling conflict: waiting for the previous deployment to stop. Keep one replica.')
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
