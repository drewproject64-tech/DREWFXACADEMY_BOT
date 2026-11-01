import unittest
import bot

class FakeAPI:
    def __init__(self):
        self.calls = []
    def call(self, method, **data):
        self.calls.append((method, data))
    def send(self, chat, text, markup=bot.MENU):
        self.calls.append(('sendMessage', {'chat_id': chat, 'text': text, 'reply_markup': markup}))

class BotTests(unittest.TestCase):
    def message(self, api, text):
        bot.handle(api, {'message': {'chat': {'id': 123, 'type': 'private'}, 'text': text}})
    def callback(self, api, data):
        bot.handle(api, {'callback_query': {'id': 'q', 'data': data, 'message': {'message_id': 1, 'chat': {'id': 123, 'type': 'private'}}}})
    def test_profile_limits(self):
        self.assertLessEqual(len(bot.ABOUT), 120)
        self.assertLessEqual(len(bot.DESCRIPTION), 512)
    def test_planner_totals(self):
        result = bot.plan(91, 3)
        self.assertIn('Session 1: 31 minutes', result)
        self.assertIn('Total elapsed time: 101 minutes', result)
        for args in [(0, 1), (10, 0), (2, 3), (1441, 2), (60, 25)]:
            with self.assertRaises(ValueError):
                bot.plan(*args)
    def test_commands_and_invalid_inputs(self):
        api = FakeAPI()
        for text in ['/start', '/help', '/about', '/privacy', '/lessons', '/quiz', 'Study planner', '/plan 90 3', '/plan x 3', '/plan 1 3', '/unknown', '/menu', '/plan@DREWFXACADEMY_BOT 90 3']:
            self.message(api, text)
            self.assertEqual(api.calls[-1][0], 'sendMessage')
    def test_all_lessons_and_quiz_answers(self):
        api = FakeAPI()
        for i, (title, _) in enumerate(bot.LESSONS):
            self.callback(api, f'lesson:{i}')
            self.assertIn(title, api.calls[-1][1]['text'])
        for i, (_, choices, correct, _) in enumerate(bot.QUESTIONS):
            self.callback(api, f'quiz:{i}')
            for answer in range(len(choices)):
                self.callback(api, f'answer:{i}:{answer}')
                self.assertIn('Correct.' if answer == correct else 'Keep practicing.', api.calls[-1][1]['text'])
        self.callback(api, 'answer:-1:0')
        self.assertIn('no longer valid', api.calls[-1][1]['text'])

if __name__ == '__main__':
    unittest.main()
