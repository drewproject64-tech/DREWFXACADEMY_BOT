"""Three local text tools for @DREWFXACADEMY_BOT."""
import json
import logging
import os
import re
import signal
import time
from urllib import request, error

NAME = 'DREW FX ACADEMY'
USERNAME = 'DREWFXACADEMY_BOT'
ABOUT = 'Free text tools: count words and characters, convert letter case and remove extra spaces directly in Telegram.'
DESCRIPTION = ('DREW FX ACADEMY provides three free text tools: '
               'Word counter: count words, characters and lines. '
               'Case converter: get uppercase and lowercase versions of your text. '
               'Space cleaner: remove extra spaces while keeping line breaks. '
               'Tap Start, choose a tool and send up to 1500 characters. '
               'Results appear directly in Telegram. No payment or channel membership is required.')
MENU = {'keyboard': [[{'text': 'Word counter'}], [{'text': 'Case converter'}], [{'text': 'Space cleaner'}]], 'resize_keyboard': True}
MODES = {'Word counter': 'count', 'Case converter': 'case', 'Space cleaner': 'clean'}
SESSIONS = {}
LIMIT = 1500
PRIVACY = ('Text and chat IDs are processed to reply. Only your chosen tool is stored in server memory for up to 30 minutes, '
           'cleared by /cancel or a restart. No text history or database is kept by this application. '
           'Telegram and the host process data under their own policies. Do not send sensitive information.')
HELP = ('Choose Word counter, Case converter or Space cleaner, then send text. '
        'You can also send /count your text, /case your text or /clean your text. '
        'Maximum: 1500 characters. /cancel clears your tool selection. /privacy explains data use.')

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

def transform(mode, text):
    if not text.strip():
        raise ValueError('Please send some text.')
    if len(text) > LIMIT:
        raise ValueError('Please send no more than 1500 characters.')
    if mode == 'count':
        return (f'Words (separated by whitespace): {len(text.split())}\n'
                f'Characters (Unicode code points, including spaces): {len(text)}\n'
                f'Lines: {len(text.splitlines())}')
    if mode == 'case':
        # Separate messages avoid overflowing Telegram after Unicode case expansion.
        return ['UPPERCASE\n' + text.upper(), 'lowercase\n' + text.lower()]
    if mode == 'clean':
        lines = [re.sub(r'[^\\S\\n]+', ' ', line).strip() for line in text.split('\n')]
        return 'Cleaned text:\n' + '\n'.join(lines).strip()
    raise ValueError('Choose a tool from the menu.')

def handle(api, update):
    now = time.monotonic()
    for key in list(SESSIONS):
        if now - SESSIONS[key][1] > 1800:
            del SESSIONS[key]
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
        api.send(chat, 'The tools have been updated. Choose one of the three text tools below.')
        return
    text = message.get('text')
    if not isinstance(text, str):
        api.send(chat, 'Please send a text message. Photos, files and voice notes are not supported.')
        return
    parts = text.split(maxsplit=1)
    cmd = parts[0].split('@')[0].lower() if parts else ''
    if cmd in ('/start', '/menu', '/cancel'):
        SESSIONS.pop(chat, None)
        api.send(chat, f'Welcome to {NAME}. Count words, convert letter case or clean extra spaces. Choose a tool, then send your text.')
    elif cmd in ('/help', '/privacy', '/about'):
        api.send(chat, {'/help': HELP, '/privacy': PRIVACY, '/about': DESCRIPTION}[cmd])
    elif text in MODES or cmd in ('/count', '/case', '/clean'):
        mode = MODES[text] if text in MODES else cmd[1:]
        if len(SESSIONS) >= 10000 and chat not in SESSIONS:
            SESSIONS.pop(next(iter(SESSIONS)))
        SESSIONS[chat] = (mode, now)
        if text not in MODES and len(parts) == 2:
            respond(api, chat, mode, parts[1])
        else:
            api.send(chat, f'{dict(count="Word counter", case="Case converter", clean="Space cleaner")[mode]} selected. Send your text (up to 1500 characters).')
    elif cmd.startswith('/'):
        api.send(chat, 'Use /count, /case or /clean, or choose a button. /help shows instructions.')
    elif chat in SESSIONS:
        mode = SESSIONS[chat][0]
        SESSIONS[chat] = (mode, now)
        respond(api, chat, mode, text)
    else:
        api.send(chat, 'Choose Word counter, Case converter or Space cleaner first, then send your text.')

def respond(api, chat, mode, text):
    try:
        result = transform(mode, text)
    except ValueError as exc:
        api.send(chat, str(exc))
        return
    for output in result if isinstance(result, list) else [result]:
        # Cap by UTF-16 length as well as Python length for Telegram's message limit.
        chunks, chunk, units = [], '', 0
        for char in output:
            size = 2 if ord(char) > 65535 else 1
            if units + size > 3500:
                chunks.append(chunk)
                chunk, units = '', 0
            chunk += char
            units += size
        if chunk:
            chunks.append(chunk)
        for chunk in chunks:
            api.send(chat, chunk)

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
        commands = [('start', 'Open the three text tools'), ('count', 'Count words and characters'), ('case', 'Convert uppercase and lowercase'), ('clean', 'Remove extra spaces'), ('cancel', 'Clear selected tool'), ('help', 'Instructions'), ('privacy', 'Data information')]
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
