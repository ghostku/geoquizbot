import os

from flask import Flask, request
from flask_redis import FlaskRedis

import telebot
import pickle

TOKEN = "915055480:AAF8d8fTTeD6QaPUs3aVOTcsUtxbTVYwTYE"
QUESTIONS = [
    {"q": "Первый вопрос он простой Ответ: _ВАУ_", "a": "ВАУ"},
    {"q": "q2", "a": "a2"},
]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.config.from_object(os.environ.get("GEOQUIZBOT", "config.DevelopmentConfig"))
storage = FlaskRedis(app)


class Question(object):
    def __init__(self, q, a):
        self.question = q
        self.answer = a

    def check_answer(self, answer):
        is_correct = answer == self.answer
        print(
            f"Correct answer: {self.answer} Your answer: {answer} So: {str(is_correct)}"
        )
        return {
            "status": is_correct,
            "message": "Правильно !!!" if is_correct else "Ответ неверный",
        }


class Questions(object):
    def __init__(self, data, id):
        if not self.load(id):
            self.questions = []
            self.id = id
            self.status = 0
            for question in data:
                self.questions.append(Question(question["q"], question["a"]))

    def load(self, id):
        try:
            data = pickle.loads(storage.get(id))
            self.questions = data.questions
            self.id = id
            self.status = data.status
        except TypeError:
            return False

    def save(self):
        storage.set(self.id, pickle.dumps(self))

    def get_current_question(self):
        print(self.status)
        return self.questions[self.status].question

    def is_first(self):
        return not (self.status)

    def is_last(self):
        return False

    def check_answer(self, answer):
        result = self.questions[self.status].check_answer(answer)
        if result['status']:
            self.status += 1
            self.save()
        return result


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello, " + message.from_user.first_name)


@bot.message_handler(commands=["reset"])
def reset(message):
    storage.delete(message.chat.id)
    bot.reply_to(message, "Состояние сброшено")


@bot.message_handler(func=lambda message: True, content_types=["text"])
def echo_message(message):
    # bot.reply_to(message, message.text + "\n" + str(message.chat.id))
    quiz = Questions(QUESTIONS, message.chat.id)
    if not quiz.is_last():
        bot.reply_to(message, quiz.check_answer(message.text)['message'])
    bot.reply_to(message, quiz.get_current_question())


@app.route("/" + TOKEN, methods=["POST"])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200


@app.route("/test/<data>")
def test(data):
    storage.set("1", data)
    return storage.get("1"), 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://geoquizbot.herokuapp.com/" + TOKEN)
    return "!", 200
