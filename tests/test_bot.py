import unittest
import bot

class API:
    def __init__(self): self.calls = []
    def call(self, method, **data): self.calls.append((method, data))
    def send(self, chat, text, markup=bot.MENU): self.calls.append(('sendMessage', {'text': text, 'reply_markup': markup}))

class Tests(unittest.TestCase):
    def setUp(self):
        bot.SESSIONS.clear()
        self.api = API()
    def msg(self, text):
        bot.handle(self.api, {'message': {'chat': {'id': 1, 'type': 'private'}, 'text': text}})
    def test_count(self):
        result = bot.transform('count', 'one two\nthree')
        self.assertIn('whitespace): 3', result)
        self.assertIn('spaces): 13', result)
        self.assertIn('Lines: 2', result)
    def test_case_and_cleanup(self):
        self.assertEqual(bot.transform('case', 'Hello')[0], 'UPPERCASE\nHELLO')
        self.assertEqual(bot.transform('case', 'Hello')[1], 'lowercase\nhello')
        self.assertEqual(bot.transform('clean', '  a   b \n c\t d  '), 'Cleaned text:\na b\nc d')
    def test_all_button_flows(self):
        for button in bot.MODES:
            self.msg(button)
            self.msg('Hello   world')
            self.assertEqual(self.api.calls[-1][0], 'sendMessage')
        self.msg('/cancel')
        self.assertNotIn(1, bot.SESSIONS)
        for command in ('/count hi there', '/case@DREWFXACADEMY_BOT Hello', '/clean hi   there', '/start campaign', '/help', '/privacy'):
            self.msg(command)
            self.assertEqual(self.api.calls[-1][0], 'sendMessage')
    def test_limits_and_unicode(self):
        for text in (' ', 'x'*1501):
            with self.assertRaises(ValueError): bot.transform('case', text)
        self.msg('/case ' + '\U0001F600'*1500)
        for method, data in self.api.calls:
            if method == 'sendMessage':
                self.assertLessEqual(len(data['text'].encode('utf-16-le'))//2, 3500)
    def test_metadata_and_old_callbacks(self):
        self.assertLessEqual(len(bot.ABOUT), 120)
        self.assertLessEqual(len(bot.DESCRIPTION), 512)
        self.assertEqual(len(bot.MENU['keyboard']), 3)
        bot.handle(self.api, {'callback_query': {'id': 'x', 'data': 'plan:60', 'message': {'chat': {'id': 1, 'type': 'private'}}}})
        self.assertIn('updated', self.api.calls[-1][1]['text'])

if __name__ == '__main__': unittest.main()
