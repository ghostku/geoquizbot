"""Класс для подсказок
"""


class Hint:
    """Класс для подсказок
    """

    def __init__(self, time, text):
        self.time = time
        self.text = text
        self.taken = False

    def get(self):
        """Выдача подсказки
        """
        self.taken = True
        return self.text
