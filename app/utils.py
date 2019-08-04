"""Утилиты
"""
import os

from _io import BufferedReader
from app import APP_SETTINGS


def get_photo(photo: str) -> BufferedReader:
    """Получения обьекта фотографии по ссылке

    Arguments:
        photo {str} -- Путь к файлу фотографии

    Returns:
        BufferedReader -- Обьект фотография
    """
    return open(os.path.join(APP_SETTINGS["IMG_DIR"], photo), "rb")
