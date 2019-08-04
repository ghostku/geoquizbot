# pylint: disable=invalid-name, wrong-import-position

"""Бот для проведения различных викторин
"""
import os
from flask import Flask
from flask_redis import FlaskRedis
import telebot


bot = telebot.TeleBot("")
storage = FlaskRedis()
APP_SETTINGS = {}

from app import models  # NOQA: E402, F401


def create_app() -> Flask:
    """Создание самого flask-приложения

    Returns:
        [flask] -- Flask-приложение
    """
    app = Flask(__name__)
    app.config.from_object(os.environ.get("GEOQUIZBOT", "config.DevelopmentConfig"))
    bot.token = app.config["TELEGRAM_BOT_TOKEN"]

    # Костыль потому как в бот нужно передать настройки а напрямую из app.config
    # бот читать не может - он в blueprint и вне контекста request
    APP_SETTINGS["ADMIN_CHAT_ID"] = app.config["ADMIN_CHAT_ID"]
    APP_SETTINGS["TELEGRAM_BOT_TOKEN"] = app.config["TELEGRAM_BOT_TOKEN"]
    APP_SETTINGS["DEFAULT_QUIZ"] = app.config["DEFAULT_QUIZ"]
    APP_SETTINGS["IMG_DIR"] = app.config["IMG_DIR"]
    APP_SETTINGS["DISTANSE_ERROR"] = app.config["DISTANSE_ERROR"]

    # Инициализируем дополнения
    storage.init_app(app)

    from app.main import bp as main_bp  # NOQA: E402
    from app.bot import bp as bot_bp  # NOQA: E402

    app.register_blueprint(main_bp)
    app.register_blueprint(bot_bp)

    return app
