import os

from flask import Flask, request

import telebot

TOKEN = '915055480:AAF8d8fTTeD6QaPUs3aVOTcsUtxbTVYwTYE'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://geoquizbot.herokuapp.com/' + TOKEN)
    return "!", 200