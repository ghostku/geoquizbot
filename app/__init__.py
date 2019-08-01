import os
from time import sleep
from flask import Flask, request
from flask_redis import FlaskRedis
from datetime import datetime

import telebot
from telebot.apihelper import ApiException, types
from haversine import haversine, Unit
import pickle

from .exif import ImageMetaData

ADMIN_CHAT_ID = 227756922
TOKEN = "752824460:AAGLdNRpc89MntcHA-jHc9qnnidXK7RHaJE"
QUESTIONS = {
    "greeting message": [
        """Приветствую вас, *Мария*!
Вы обратились в службу поддержки роботизированной системы доставки подарков CyberPost.
Наш девиз: *Киииииборги - они доставляют*
Оставайтесь на линии, первый доступный оператор ответит Вам
""",
        """Здраствуйте, Мария!
Служба поддержки, оператор Ы413. Чем могу помочь?""",
        "О, я вижу что для вас есть подарок. У вас день рождения. Поздравляем. Секундочку я уточню данные по вашей доставке...",
        "Хм, Мария, случилась непоправимая ошибка. К сожалению на некоторых участках доставки мы всё еще используем биологические механизмы. Так вот один из них, серийный номер МИХАИЛ, пропал вместе с вашей посылкой. Я всегда говорил начальству Это же люди, им нельзя доверять. Наверной Ваш подарок утерян. Нам очень жаль ...",
        """Мария, Вы еще тут?
Кажется не все так плохо, у всех наших биологических курьеров вместо глаза вклеена фотокамера, ну чтобы мы могли ослеживать их перемещения. Я думаю смогу предоставить вам снимки с камеры курьера и вам нужно будет всего лишь проследить за его перемещениями и возможно вы сможете найти свой подарок. Готовы?""",
        """Пока готовятся фотографии подскажу вам немного:

- Вам нужно стать на точку откуда был сделан снимок
- Мы заставляем курьеров делать частые снимки поэтому расстояние между фотографиями не превышает 200 метров
- Ваши человеческие устройства которые Вы используете для навигации неточны, поэтому если система не принимает ваше местонахождение а Вы уверены что нашли место верно - подождите пару секунд и попробуйте еще раз""",
        "Ну что ж в путь",
    ],
    "questions": [
        {"q": "q2", "a": "a2", "img": "1.jpg", "type": "geo"},
        {"q": "Первый вопрос он простой Ответ: _ВАУ_", "a": "1", "type": "text"},
        {"q": "второй вопрос он простой Ответ: _ВАУ_", "a": "2", "type": "text"},
    ],
}
QUESTIONS = {
    "greeting message": [
        """Привет
"""
    ],
    "farevell message": [
        {"text": "Поздравляем Вы справились"},
        {"text": "Вы вернули нам веру в человечество"},
        {"text": "Идите и заберите свой подарок", "img": "finish.jpg"}
        ],
    "questions": [
        {
            "q": "Прежде чем мы начнём мы должны удостоверится что вы это вы. Введите пожалуйста имеющийся у Вас код. Код нанесён зелеными чернилами состоит из латинской буквы 8-и цифр и еще одной латинской буквы. Шучу-шучу это же не квест какой-то правда ;) УДАЧИ",
            "a": "B06586435A",
            "type": "text",
            "helps": [
                {"time": 60, "text": "Кстати наша организация работает не бесплатно"},
                {
                    "time": 120,
                    "text": "Доставка обойдеться вам в $2. У вас хоть есть такие деньги?",
                },
            ],
        },
        {"img": "IMG_20190726_175755.jpg", "type": "geo"},
        {"img": "IMG_20190726_180502.jpg", "type": "geo"},
        # {"img": "IMG_20190726_180757.jpg", "type": "geo"},
        # {"img": "IMG_20190726_181045.jpg", "type": "geo"},
        # {"img": "IMG_20190726_181237.jpg", "type": "geo"},
        # {"img": "IMG_20190726_181654.jpg", "type": "geo"},
        # {"img": "IMG_20190726_181947.jpg", "type": "geo"},
        # {"img": "IMG_20190726_182037.jpg", "type": "geo"},
        # {"img": "IMG_20190726_182150.jpg", "type": "geo"},
        # {"img": "IMG_20190726_182330.jpg", "type": "geo"},
        # {"img": "IMG_20190726_183123.jpg", "type": "geo"},
        # {"img": "IMG_20190726_183209.jpg", "type": "geo"},
        # {"img": "IMG_20190726_183718.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184005.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184108.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184257.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184420.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184524.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184539.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184658.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184831.jpg", "type": "geo"},
        # {"img": "IMG_20190726_184925.jpg", "type": "geo"},
        # {"img": "IMG_20190726_185207.jpg", "type": "geo"},
        # {"img": "IMG_20190726_185358.jpg", "type": "geo"},
        # {"img": "IMG_20190726_185520.jpg", "type": "geo"},
        # {"img": "IMG_20190726_185614.jpg", "type": "geo"},
        # {"img": "IMG_20190726_185717.jpg", "type": "geo"},
    ],
}
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
    def __init__(self, data, id):
        if not self.load(id):
            print("New load")
            self.questions = []
            self.id = id
            self.status = "READY"
            self.last_question = 0
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
                    self.questions.append(
                        GeoQuestion(question["img"])
                    )
            self.greeting_message = data.get("greeting message", "Hi")
            self.farevell_message = data.get("farevell message", "Bye")

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
            if 'img' in message:
                photo = open(os.path.join(app.config["IMG_DIR"], message['img']), "rb")
                bot.send_photo(chat_id, photo, caption=message['text'])
            else:
                bot.send_message(chat_id, message['text'], parse_mode='Markdown')
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
        users_list = pickle.loads(storage.get('users'))
    except TypeError:
        users_list = set()
    users_list.add(message.chat.id)
    storage.set('users', pickle.dumps(users_list))

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

@bot.message_handler(commands=["wow"])
def wow(message):
    quiz = Questions(QUESTIONS, message.chat.id)
    quiz.finish(message.chat.id)

@bot.message_handler(func=lambda message: True, content_types=["text", "location"])
def echo_message(message):
    print(f'Chat ID: {message.chat.id}')
    if ((message.chat.id == ADMIN_CHAT_ID) and (message.content_type == 'text')):
        print('You are an admin')
        if message.text.startswith('users'):
            print(', '.join([str(i) for i in pickle.loads(storage.get('users'))]))
            bot.reply_to(message, '\n'.join([str(i) for i in pickle.loads(storage.get('users'))]))
            return
        elif message.text.startswith('skip'):
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


@app.route("/test/<data>")
def test(data):
    storage.set("1", data)
    return storage.get("1"), 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=app.config["WEB_HOOK_URL"] + TOKEN)
    return "!", 200
