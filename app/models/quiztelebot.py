# pylint: disable=no-self-use

"""Враппер для подключения ввода/вывода
"""
from time import sleep

from app import bot
from app.utils import get_photo
from telebot import types

from .hint import Hint


class QuizTeleBot:
    """Враппер для подключения вывода
    """

    def __init__(self, chat_id, multimessages_delay=10):
        self.chat_id = chat_id
        self.multimessages_delay = multimessages_delay

    def send_messages(self, messages: list):
        """Отправляет набор сообщений

        Arguments:
            messages {list} -- Сообщения
        """
        for message in messages:
            if "img" in message:
                photo = get_photo(message["img"])
                bot.send_photo(self.chat_id, photo, caption=message["text"])
            else:
                bot.send_message(
                    self.chat_id,
                    message["text"],
                    parse_mode="Markdown",
                    reply_markup=types.ReplyKeyboardRemove(),
                )
            sleep(self.multimessages_delay)

    def send_correct_answer(self, message: types.Message, text="Правильно!!"):
        """Отправляет уведомление о правильном ответе

        Arguments:
            message {types.Message} -- [Сообщение на которое нужно ответить]

        Keyword Arguments:
            text {str} -- [Текст ответа] (default: {"Правильно!!"})
        """
        bot.reply_to(message, text, reply_markup=types.ReplyKeyboardRemove())

    def send_wrong_answer(self, message: types.Message, text="Неправильно :("):
        """Отправляет уведомление о неправильном ответе

        Arguments:
            message {types.Message} -- [Сообщение на которое нужно ответить]

        Keyword Arguments:
            text {str} -- [Текст ответа] (default: {"Правильно!!"})
        """
        bot.reply_to(message, text, reply_markup=types.ReplyKeyboardRemove())

    def show_hint(self, message: types.Message, hint: Hint):
        """Вывод подсказки

        Arguments:
            message {types.Message} -- Сообщение с опросом на которое нужно ответить
            hint {Hint} -- Подсказка
        """
        bot.reply_to(message, hint.get(), reply_markup=types.ReplyKeyboardRemove())

    def ask_question(self, question: str, photo=None, location=False):
        """Выводит вопрос. Поведение отличается для вопросов в которых есть
        картинка или для вопросов которые подразумевают ответ геопозицией

        Arguments:
            question {str} -- Текст вопроса

        Keyword Arguments:
            photo {[type]} -- Картинка (default: {None})
            location {[type]} -- Требуется ли ответ с геопозицией (default: {False:bool})
        """
        keyboard = None
        if location:
            keyboard = types.ReplyKeyboardMarkup()
            keyboard.add(types.KeyboardButton(text="Я на месте", request_location=True))
        if photo:
            bot.send_photo(self.chat_id, photo, caption=question, reply_markup=keyboard)
        else:
            bot.send_message(self.chat_id, question, reply_markup=keyboard)
