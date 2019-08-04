# pylint: disable=invalid-name, wrong-import-position

""" Непосредственно команды которые работают с ботом
"""
from flask import Blueprint

bp = Blueprint("bot", __name__)

from app.bot import endpoints  # NOQA E401, F401
