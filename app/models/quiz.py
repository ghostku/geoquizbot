# pylint: disable=invalid-name

"""Класс квиза
"""
import json
import pickle

from app import storage
from telebot.apihelper import types

from .locationquestion import LocationQuestion
from .question import Question
from .quiztelebot import QuizTeleBot


class Quiz:
    """Класс квиза
    """

    def __init__(self, game_id, filename=None):
        if not self.load(game_id):
            print("New game")
            self.questions = []
            self.game_id = game_id
            self.status = "READY"
            self.last_question = 0
            self.io = QuizTeleBot(self.game_id)

            if filename:
                self.load_from_file(filename)

    def load_from_file(self, filename: str):
        """Load object from JSON file

        Arguments:
            filename {str} -- File name with path
        """
        print("Loading data from JSON file")
        data = json.load(open(filename, "r", encoding="utf-8"))
        self.greeting_message = data.get("greeting message", "Hi")
        self.farevell_message = data.get("farevell message", "Bye")
        for question in data["questions"]:
            if question["type"] == "text":
                self.questions.append(
                    Question(
                        question["q"],
                        question["a"],
                        wrapper=self.io,
                        hints=question.get("helps", []),
                    )
                )
            elif question["type"] == "geo":
                self.questions.append(
                    LocationQuestion(question["img"], wrapper=self.io)
                )

    def load(self, game_id: int) -> bool:
        """Загрузка ранее сохраненной игры

        Arguments:
            game_id {int} -- ID игры

        Returns:
            bool -- Удалось ли загрузить?
        """

        try:
            print("Getting from REDIS")
            data = pickle.loads(storage.get(game_id))
            self.questions = data.questions
            self.game_id = game_id
            self.status = data.status
            self.last_question = data.last_question
            self.greeting_message = data.greeting_message
            self.farevell_message = data.farevell_message
            return True
        except TypeError:
            print("No data in REDIS")
            return False

    def save(self):
        """Сохранение текущей игры
        """
        storage.set(self.game_id, pickle.dumps(self))

    def ask_current_question(self):
        """Задать текущий вопрос
        """
        self.questions[self.last_question].ask_question()

    def check_answer(self, message: types.Message) -> bool:
        """Проверка правильности ответа

        Arguments:
            message {types.Message} -- Сообщение с ответом

        Returns:
            bool -- Правильный ли был ответ
        """

        result = self.questions[self.last_question].check_answer(message)
        if result:
            self.last_question += 1
            if self.last_question >= len(self.questions):
                self.finish()
        self.save()
        return result

    def is_in_process(self) -> bool:
        """Начата ли игра

        Returns:
            bool -- Начата ли игра
        """
        return self.status == "WORKING"

    def send_greeting(self):
        """Отправка приветственного сообщения
        """
        self.io.send_messages(self.greeting_message)

    def send_finish(self):
        """Отправка финального сообщения
        """
        self.io.send_messages(self.farevell_message)

    def start(self):
        """Начать игру
        """
        self.send_greeting()
        self.status = "WORKING"
        self.ask_current_question()
        self.save()

    def finish(self):
        """Закончить игру
        """
        self.send_finish()
        self.status = "FINISH"
        self.save()

    def force_next_answer(self):
        """Следующий ответ будет признан верным
        """
        self.questions[self.last_question].force_next_answer()
        self.save()
