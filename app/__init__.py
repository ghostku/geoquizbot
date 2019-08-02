import os
from time import sleep
from flask import Flask, request
from flask_redis import FlaskRedis
from datetime import datetime
import json
import telebot
from telebot.apihelper import ApiException, types
from haversine import haversine, Unit
import pickle

from .exif import ImageMetaData

ADMIN_CHAT_ID = 227756922
TOKEN = "752824460:AAGLdNRpc89MntcHA-jHc9qnnidXK7RHaJE"
# QUESTIONS = 
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.config.from_object(os.environ.get("GEOQUIZBOT", "config.DevelopmentConfig"))
storage = FlaskRedis(app)


class Help(object):
    def __init__(self, time, text):
        self.time = time
        self.text = text
        self.taken = False


class Question(object):
    def __init__(self, q="", a="", helps=[], first_time_answer=None):
        self.question = q
        self.answer = a
        self.answers_given = 0
        self.first_time_answer = first_time_answer
        self.helps = []
        self._force_next_answer = False
        for help in helps:
            self.helps.append(Help(help["time"], help["text"]))

    def check_answer(self, message):
        is_correct = (message.text == self.answer) or self._force_next_answer
        self.answers_given += 1
        print(
            f"Correct answer: {self.answer} Your answer: {message.text} So: {str(is_correct)}"
        )
        bot.reply_to(
            message,
            "Правильно!!" if is_correct else "Ответ неверный",
            reply_markup=types.ReplyKeyboardRemove(),
        )

        self.show_help(message)
        return is_correct

    def force_next_answer(self):
        self._force_next_answer = True

    def show_help(self, message):
        now = datetime.now()

        print(now)

        if not self.first_time_answer:
            print("First Answer")
            self.first_time_answer = now
        else:
            difference = (now - self.first_time_answer).total_seconds()
            print(f"Difference is: {difference}")
            for help in self.helps:
                if help.time < difference and not help.taken:
                    bot.reply_to(
                        message, help.text, reply_markup=types.ReplyKeyboardRemove()
                    )
                    help.taken = True

    def ask_question(self, chat_id):
        bot.send_message(chat_id, self.question)


class GeoQuestion(Question):
    def __init__(self, img, first_time_answer=None):
        # self.question = q
        # self.answer = a
        # self.answers_given = 0
        super(GeoQuestion, self).__init__()
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
        meta_Data = ImageMetaData(os.path.join(app.config["IMG_DIR"], self.image))
        correct_coord = meta_Data.get_lat_lng()
        distance = haversine(test_coord, correct_coord, Unit.METERS)
        is_correct = (distance <= 10) or self._force_next_answer
        if is_correct:
            bot.reply_to(
                message, "Вы на верному пути", reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            bot.reply_to(message, f"К сожалению до цели осталось еще {distance} метров")

        return is_correct


class Questions(object):
    def __init__(self, id, filename=None):
        if not self.load(id):
            print("New load")
            self.questions = []
            self.id = id
            self.status = "READY"
            self.last_question = 0

            if filename:
                self.load_from_file(filename)

    def load_from_file(self, filename: str):
        """Load object from JSON file
        
        Arguments:
            filename {str} -- File name with path
        """
    
        data = json.load(open(filename, 'r', encoding='utf-8'))
        self.greeting_message = data.get("greeting message", "Hi")
        self.farevell_message = data.get("farevell message", "Bye")
        for question in data["questions"]:
                if question["type"] == "text":
                    self.questions.append(
                        Question(
                            question["q"],
                            question["a"],
                            helps=question.get("helps", []),
                        )
                    )
                elif question["type"] == "geo":
                    self.questions.append(GeoQuestion(question["img"]))
            

    def load(self, id):
        try:
            print("Getting from redis")
            data = pickle.loads(storage.get(id))
            self.questions = data.questions
            self.id = id
            self.status = data.status
            self.last_question = data.last_question
            self.greeting_message = data.greeting_message
            self.farevell_message = data.farevell_message
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
            if self.last_question >= len(self.questions):
                print("Was the last question")
                self.finish(message.chat.id)
        self.save()
        return result

    def is_in_process(self):
        return self.status == "WORKING"

    def send_greeting(self, chat_id):
        # bot.send_message(chat_id, "Приветственное сообщение")
        for message in self.greeting_message:
            bot.send_message(
                chat_id,
                message,
                parse_mode="Markdown",
                reply_markup=types.ReplyKeyboardRemove(),
            )
            sleep(10)

    def send_messages(self, chat_id, messages):
        for message in messages:
            print(messages)
            print(message)
            if "img" in message:
                photo = open(os.path.join(app.config["IMG_DIR"], message["img"]), "rb")
                bot.send_photo(chat_id, photo, caption=message["text"])
            else:
                bot.send_message(chat_id, message["text"], parse_mode="Markdown")
            sleep(10)

    def send_finish(self, chat_id):
        self.send_messages(chat_id, self.farevell_message)

    def start(self, chat_id):
        self.send_greeting(chat_id)
        self.status = "WORKING"
        self.ask_current_question(chat_id)
        self.save()

    def finish(self, chat_id):
        self.send_finish(chat_id)
        self.status = "FINISH"
        self.save()

    def force_next_answer(self):
        self.questions[self.last_question].force_next_answer()
        self.save()


@bot.message_handler(commands=["start"])
def start(message):
    # bot.reply_to(message, "Hello, " + message.from_user.first_name)
    try:
        users_list = pickle.loads(storage.get("users"))
    except TypeError:
        users_list = set()
    users_list.add(str(message.chat.id) + " " + str(datetime.now()))
    storage.set("users", pickle.dumps(users_list))

    storage.delete(message.chat.id)
    quiz = Questions(message.chat.id, app.config['DEFAULT_QUIZ'])
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
    print(f"Chat ID: {message.chat.id}")
    if (message.chat.id == ADMIN_CHAT_ID) and (message.content_type == "text"):
        print("You are an admin")
        if message.text.startswith("users"):
            print(", ".join([str(i) for i in pickle.loads(storage.get("users"))]))
            bot.reply_to(
                message, "\n".join([str(i) for i in pickle.loads(storage.get("users"))])
            )
            return
        elif message.text.startswith("skip"):
            game_id = message.text.split()[-1]
            quiz = Questions(QUESTIONS, game_id)
            quiz.force_next_answer()
            return

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


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=app.config["WEB_HOOK_URL"] + TOKEN)
    return "!", 200
