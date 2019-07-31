import os

from flask import Flask, request
from flask_redis import FlaskRedis

import telebot
from telebot.apihelper import ApiException, types
import pickle

TOKEN = "915055480:AAF8d8fTTeD6QaPUs3aVOTcsUtxbTVYwTYE"
QUESTIONS = [
    {"q": "Первый вопрос он простой Ответ: _ВАУ_", "a": "ВАУ", "type": "text"},
    {"q": "q2", "a": "a2", "img": "1.jpg", "type": "geo"},
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

    def ask_question(self, chat_id):
        bot.send_message(chat_id, self.question)


class GeoQuestion(Question):
    def __init__(self, q, a, img):
        self.question = q
        self.answer = a
        self.image = img

    def ask_question(self, chat_id):
        bot.send_message(chat_id, self.question + "\n" + self.image)
        bot.send_message(
            chat_id,
            self.question + "\n" + os.path.join(app.config["IMG_DIR"], self.image),
        )
        photo = open(os.path.join(app.config["IMG_DIR"], self.image), "rb")
        keyboard = types.ReplyKeyboardMarkup()
        keyboard.add(types.KeyboardButton(text="Я на месте", request_location=True))
        bot.send_photo(
            chat_id, photo, caption="Найдите место сьемки", reply_markup=keyboard
        )


class Questions(object):
    def __init__(self, data, id):
        if not self.load(id):
            print("New load")
            self.questions = []
            self.id = id
            self.status = 0
            for question in data:
                if question["type"] == "text":
                    self.questions.append(Question(question["q"], question["a"]))
                elif question["type"] == "geo":
                    self.questions.append(
                        GeoQuestion(question["q"], question["a"], question["img"])
                    )

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

    def ask_current_question(self, chat_id):
        # print(self.status)
        self.questions[self.status].ask_question(chat_id)
        # return self.questions[self.status].question

    def is_first(self):
        return not (self.status)

    def is_last(self):
        return False

    def check_answer(self, answer):
        print(f"Current status is: {self.status}")
        result = self.questions[self.status].check_answer(answer)
        if result["status"]:
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
    quiz = Questions(QUESTIONS, message.chat.id)
    if not quiz.is_last():
        bot.reply_to(message, quiz.check_answer(message.text)["message"])
    quiz.ask_current_question(message.chat.id)


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
