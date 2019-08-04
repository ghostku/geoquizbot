# pylint: disable=invalid-name

"""Класс вопроса/задания
"""
from datetime import datetime

from .hint import Hint


class Question:
    """Класс вопроса/задания
    """

    def __init__(self, q="", a="", wrapper=None, hints=None):
        hints = hints or []
        self.question = q
        self.answer = a
        self.start_time = None
        self.hints = []
        self._force_next_answer = False
        self.io = wrapper
        for hint in hints:
            self.hints.append(Hint(hint["time"], hint["text"]))

    def check_answer(self, message) -> bool:
        """
        Проверяет поданный ответ на правильность

        Arguments:
            message {str} -- Сообщение с ответом

        Returns:
            bool -- Верен ли ответ
        """

        is_correct = (message.text == self.answer) or self._force_next_answer
        if is_correct:
            self.io.send_correct_answer(message)
        else:
            self.io.send_wrong_answer(message)
        self.show_hints(message)
        return is_correct

    def force_next_answer(self):
        """Следующий вариант ответа будет признан верным
        """
        self._force_next_answer = True

    def show_hints(self, message):
        """
        Проверяем не нужно ли показать подсказку и
        показываем если прошло достаточно времени

        Arguments:
            message {[type]} -- ссылка на сообщение
        """
        now = datetime.now()

        if not self.start_time:
            self.start_time = now
            return

        difference = (now - self.start_time).total_seconds()
        for hint in self.hints:
            if hint.time < difference and not hint.taken:
                self.io.show_hint(message, hint)

    def ask_question(self):
        """Задаем вопрос
        """
        self.io.ask_question(self.question)
