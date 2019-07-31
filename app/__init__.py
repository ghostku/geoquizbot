import os

from flask import Flask, request
from flask_redis import FlaskRedis

import telebot
from telebot.apihelper import ApiException, types
from haversine import haversine, Unit
import pickle

from .exif import ImageMetaData

TOKEN = "915055480:AAF8d8fTTeD6QaPUs3aVOTcsUtxbTVYwTYE"
QUESTIONS = {
    "questions": [
        {"q": "q2", "a": "a2", "img": "1.jpg", "type": "geo"},
        {"q": "Первый вопрос он простой Ответ: _ВАУ_", "a": "1", "type": "text"},
        {"q": "второй вопрос он простой Ответ: _ВАУ_", "a": "2", "type": "text"},
    ]
    # {"q": "q2", "a": "a2", "img": "1.jpg", "type": "geo"},
}

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.config.from_object(os.environ.get("GEOQUIZBOT", "config.DevelopmentConfig"))
storage = FlaskRedis(app)


class Question(object):
    def __init__(self, q, a):
        self.question = q
        self.answer = a
        self.answers_given = 0

    def check_answer(self, message):
        is_correct = message.text == self.answer
        self.answers_given += 1
        print(
            f"Correct answer: {self.answer} Your answer: {message.text} So: {str(is_correct)}"
        )
        bot.reply_to(message, "Правильно!!" if is_correct else "Ответ неверный", reply_markup=types.ReplyKeyboardRemove())
        return is_correct

    def ask_question(self, chat_id):
        bot.send_message(chat_id, self.question)


class GeoQuestion(Question):
    def __init__(self, q, a, img):
        self.question = q
        self.answer = a
        self.answers_given = 0
        self.image = img

    def ask_question(self, chat_id):
        photo = open(os.path.join(app.config["IMG_DIR"], self.image), "rb")
        keyboard = types.ReplyKeyboardMarkup()
        keyboard.add(types.KeyboardButton(text="Я на месте", request_location=True))
        bot.send_photo(
            chat_id, photo, caption="Найдите место сьемки", reply_markup=keyboard
        )

    def check_answer(self, message):
        test_coord = (message.location.latitude, message.location.longitude)
        print(test_coord)
        meta_Data = ImageMetaData(os.path.join(app.config["IMG_DIR"], self.image))
        correct_coord = meta_Data.get_lat_lng()
        distance = haversine(test_coord, correct_coord, Unit.METERS)
        print(distance)
        is_correct = (distance <= 10)
        if is_correct:
            bot.reply_to(message, "Вы на верному пути", reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.reply_to(message, f"К сожалению до цели осталось еще {distance} метров")
            
        return is_correct

class Questions(object):
    def __init__(self, data, id):
        if not self.load(id):
            print("New load")
            self.questions = []
            self.id = id
            self.status = "READY"
            self.last_question = 0
            for question in data["questions"]:
                if question["type"] == "text":
                    self.questions.append(Question(question["q"], question["a"]))
                elif question["type"] == "geo":
                    self.questions.append(
                        GeoQuestion(question["q"], question["a"], question["img"])
                    )

    def load(self, id):
        try:
            print("Getting from redis")
            data = pickle.loads(storage.get(id))
            self.questions = data.questions
            self.id = id
            self.status = data.status
            self.last_question = data.last_question
            return True
        except TypeError:
            return False

    def save(self):
        storage.set(self.id, pickle.dumps(self))

    def ask_current_question(self, chat_id):
        self.questions[self.last_question].ask_question(chat_id)

    def is_first(self):
        return not (self.last_question)

    def is_last(self):
        return False

    def check_answer(self, message):
        print(f"Current status is: {self.status}")
        print(f"Current last question is: {self.last_question}")

        result = self.questions[self.last_question].check_answer(message)
        if result:
            self.last_question += 1
            self.save()
            if self.last_question >= len(self.questions):
                print("Was the last question")
                self.finish(message.chat.id)
        return result

    def is_in_process(self):
        return self.status == "WORKING"

    def send_greeting(self, chat_id):
        bot.send_message(chat_id, "Приветственное сообщение")

    def send_finish(self, chat_id):
        bot.send_message(chat_id, "Прощальное сообщение")

    def start(self, chat_id):
        self.send_greeting(chat_id)
        self.status = "WORKING"
        self.ask_current_question(chat_id)
        self.save()

    def finish(self, chat_id):
        self.send_finish(chat_id)
        self.status = "FINISH"
        self.save()


@bot.message_handler(commands=["start"])
def start(message):
    # bot.reply_to(message, "Hello, " + message.from_user.first_name)
    storage.delete(message.chat.id)
    quiz = Questions(QUESTIONS, message.chat.id)
    quiz.start(message.chat.id)


@bot.message_handler(commands=["reset"])
def reset(message):
    storage.delete(message.chat.id)
    bot.reply_to(message, "Состояние сброшено")

@bot.message_handler(commands=["reask"])
def reask(message):
    quiz = Questions(QUESTIONS, message.chat.id)
    quiz.ask_current_question(message.chat.id)


@bot.message_handler(func=lambda message: True, content_types=["text", "location"])
def echo_message(message):
    quiz = Questions(QUESTIONS, message.chat.id)
    if quiz.is_in_process():
        if quiz.check_answer(message):
            if quiz.is_in_process():
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
    bot.set_webhook(url=app.config["WEB_HOOK_URL"] + TOKEN)
    return "!", 200
