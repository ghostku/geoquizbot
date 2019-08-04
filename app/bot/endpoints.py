# pylint: disable=bad-continuation, no-else-return

"""Эндпоинты для бота
"""
import pickle

from app import APP_SETTINGS, bot, storage
from app.models import Players, Quiz


@bot.message_handler(commands=["start"])
def start(message):
    """Начать игру

    Arguments:
        message {[type]} -- telebot.types.Message
    """

    players = Players()
    players.add(message.chat.id)

    storage.delete(message.chat.id)
    quiz = Quiz(message.chat.id, APP_SETTINGS["DEFAULT_QUIZ"])
    quiz.start()


@bot.message_handler(commands=["reset"])
def reset(message):
    """Сбросить свою текущую игру

    Arguments:
        message {[type]} -- telebot.types.Message
    """

    storage.delete(message.chat.id)
    bot.reply_to(message, "Состояние сброшено")


@bot.message_handler(commands=["reask"])
def reask(message):
    """Повторить последний вопрос

    Arguments:
        message {[type]} -- telebot.types.Message
    """

    quiz = Quiz(message.chat.id, APP_SETTINGS["DEFAULT_QUIZ"])
    quiz.ask_current_question()


@bot.message_handler(func=lambda message: True, content_types=["text", "location"])
def echo_message(message):
    """Основная функция обработки сообщений - ответов

    Arguments:
        message {[type]} -- telebot.types.Message
    """

    # TODO: Вынести реакцию на Админа в отдельную команду
    if (message.chat.id == APP_SETTINGS["ADMIN_CHAT_ID"]) and (
        message.content_type == "text"
    ):
        print("You are an admin")
        if message.text.startswith("users"):
            print(", ".join([str(i) for i in pickle.loads(storage.get("users"))]))
            bot.reply_to(
                message, "\n".join([str(i) for i in pickle.loads(storage.get("users"))])
            )
            return
        elif message.text.startswith("skip"):
            game_id = message.text.split()[-1]
            quiz = Quiz(game_id, APP_SETTINGS["DEFAULT_QUIZ"])
            quiz.force_next_answer()
            return

    quiz = Quiz(message.chat.id, APP_SETTINGS["DEFAULT_QUIZ"])

    if quiz.is_in_process():
        if quiz.check_answer(message):
            if quiz.is_in_process():
                quiz.ask_current_question(message.chat.id)
