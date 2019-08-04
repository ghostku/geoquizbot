"""Класс вопроса про локацию
"""

import os

from app import APP_SETTINGS
from app.exif import ImageMetaData
from app.utils import get_photo
from haversine import Unit, haversine

from .question import Question


class LocationQuestion(Question):
    """Класс вопроса про локацию

    Arguments:
        Question {[type]} -- Бащовый класс вопроса
    """

    def __init__(self, img, **kwargs):
        super(LocationQuestion, self).__init__(**kwargs)
        self.image = img

    def ask_question(self):
        """Задаем вопрос
        """
        photo = get_photo(self.image)
        self.io.ask_question("Найдите место сьемки", photo, True)

    def check_answer(self, message) -> bool:
        """Проверяет поданный ответ на правильность

        Arguments:
            message {str} -- Сообщение с ответом

        Returns:
            bool -- Верен ли ответ
        """
        test_coord = (message.location.latitude, message.location.longitude)
        meta_data = ImageMetaData(os.path.join(APP_SETTINGS["IMG_DIR"], self.image))
        correct_coord = meta_data.get_lat_lng()
        distance = haversine(test_coord, correct_coord, Unit.METERS)
        is_correct = (
            distance <= APP_SETTINGS["DISTANSE_ERROR"]
        ) or self._force_next_answer
        if is_correct:
            self.io.send_correct_answer(message, text="Вы на верному пути")
        else:
            self.io.send_wrong_answer(
                message, text=f"К сожалению до цели осталось еще {distance} метров"
            )

        return is_correct
