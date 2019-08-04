# pylint: disable=invalid-name, wrong-import-position

"""Основной модуль
"""
from flask import Blueprint

bp = Blueprint("main", __name__)

from app.main import routes  # NOQA: E401, F401
