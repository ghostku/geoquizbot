"""Класс для записи все текущих игровых сессий
"""

import pickle

from app import storage


class Players:
    """Класс для записи все текущих игровых сессий
    """

    def __init__(self):
        self.redis_id = "users"  # TODO: Вынести в конфиг
        self.users_list = set()
        self.load()

    def save(self):
        """Сохраняем состояние
        """
        storage.set(self.redis_id, pickle.dumps(self.users_list))

    def load(self):
        """
        Загружаем состояние
        При неудаче создаем с нуля
        """
        try:
            self.users_list = pickle.loads(storage.get(self.redis_id))
        except TypeError:
            self.users_list = set()

    def add(self, chat_id: int):
        """Добавляем  игровую сессию в список

        Arguments:
            chat_id {int} -- ID сессии
        """
        self.users_list.add(chat_id)
        self.save()
