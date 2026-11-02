import unittest
import bot

class FakeAPI:
    def __init__(self):
        self.calls = []
    def call(self, method, **data):
        self.calls.append((method, data))
    def send(self, chat, text, markup=bot.MENU):
        self.calls.append(('sendMessage', dict(chat_id=chat, text=text, reply_markup=markup)))

class BotTests(unittest.TestCase):
    def message(self, api, text):
        bot.handle(api, {'message': {'chat': {'id': 123, 'type': 'private'}, 'text': text}})
    def callback(self, api, data):
        bot.handle(api, {'callback_query': {'id': 'q', 'data': data, 'message': {'chat': {'id': 123, 'type': 'private'}}}})
    def test_three_tools_and_commands(self):
        self.assertEqual(len(bot.MENU['keyboard']), 3)
        api = FakeAPI()
        for text in ['/start', '/start campaign', '/lessons', '/quiz', '/plan', 'Lessons', 'Quick quiz', 'Study calculator', '/help', '/privacy', '/about', '/unknown', '', '/plan@DREWFXACADEMY_BOT 60']:
            self.message(api, text)
            self.assertEqual(api.calls[-1][0], 'sendMessage')
    def test_quiz_buttons_and_answers(self):
        api = FakeAPI()
        self.message(api, 'Quick quiz')
        rows = api.calls[-1][1]['reply_markup']['inline_keyboard']
        self.assertEqual(len(rows), 3)
        for index, (_, options, correct, explanation) in enumerate(bot.QUESTIONS):
            for choice in range(3):
                self.callback(api, f'quiz:{index}:{choice}')
                self.assertIn(options[correct], api.calls[-1][1]['text'])
                self.assertIn(explanation, api.calls[-1][1]['text'])
        self.callback(api, 'quiz:-1:0')
        self.assertIn('new question', api.calls[-1][1]['text'])
    def test_calculator(self):
        api = FakeAPI()
        for n in (30, 60, 90):
            self.callback(api, f'plan:{n}')
            self.assertIn(f'Total including break: {n}', api.calls[-1][1]['text'])
        for text in ['/plan abc', '/plan -1', '/plan 60 3', '/plan 0']:
            self.message(api, text)
            self.assertIn('Choose your total study time', api.calls[-1][1]['text'])
    def test_old_buttons_and_expired_callback(self):
        class ExpiredAPI(FakeAPI):
            def call(self, method, **data):
                raise bot.APIError(400)
        api = ExpiredAPI()
        self.callback(api, 'plan:60')
        self.assertIn('60-minute', api.calls[-1][1]['text'])
        self.callback(api, 'answer:0:1')
        self.assertIn('older button', api.calls[-1][1]['text'])
    def test_profile_limits(self):
        self.assertLessEqual(len(bot.ABOUT), 120)
        self.assertLessEqual(len(bot.DESCRIPTION), 512)

if __name__ == '__main__':
    unittest.main()
