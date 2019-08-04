"""Маршруты основного модуля
"""
import telebot
from app import bot
from app.main import bp
from flask import current_app, request


@bp.route("/setwebhook", methods=["POST"])
def get_message():
    """Endpoint для работы webhook'а от telegram
    """
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200


@bp.route("/")
def webhook():
    """Установка webhook'a
    """
    bot.remove_webhook()
    bot.set_webhook(url=current_app.config["WEB_HOOK_URL"] + "setwebhook")
    return "!", 200
