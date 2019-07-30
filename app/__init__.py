import os

from flask import Flask, request
from flask_redis import FlaskRedis

import telebot

TOKEN = "915055480:AAF8d8fTTeD6QaPUs3aVOTcsUtxbTVYwTYE"
QUESTIONS = [{"q": "q1", "a": "a1"}, {"q": "q2", "a": "a2"}]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.config.from_object(os.environ.get("GEOQUIZBOT", "config.DevelopmentConfig"))
storage = FlaskRedis(app)


class Question(object):
    def __init__(self, q, a):
        self.question = q
        self.answer = a


class Questions(object):
    def __init__(self, data, id):
        self.questions = []
        self.id = id
        for question in data:
            self.questions.append(Question(question["q"], question["a"]))
        self.load_status()

    def load_status(self):
        try:
            self.status = int(storage.get(self.id))
        except TypeError:
            self.status = 0

    def save_status(self):
        storage.set(self.id, self.status)

    def get_current_question(self):
        return self.questions[self.status].question
    
    def is_first(self):
        return not(self.status)
    
    def check_answer(self, answer):
        print(answer)
        return False


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello, " + message.from_user.first_name)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def echo_message(message):
    # bot.reply_to(message, message.text + "\n" + str(message.chat.id))
    quiz = Questions(QUESTIONS, message.chat.id)
    if not quiz.is_first():
        quiz.check_answer()
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
