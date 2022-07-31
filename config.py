import os


class Config(object):
    """Base class for configuration."""

    # Определяет включен ли режим отладки
    DEBUG = False

    # Включение защиты против "Cross-site Request Forgery (CSRF)"
    CSRF_ENABLED = True

    # Случайный ключ, которые будет исползоваться для подписи
    # данных, например cookies.
    SECRET_KEY = "FSdf4f444D4443sd_!5GSD"

    basedir = os.path.abspath(os.path.dirname(__file__))
    dbdir = os.path.join(basedir, "data/db")
    IMG_DIR = os.path.join(basedir, "data/imgs")
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(dbdir, "gbot.db")
    # SQLALCHEMY_MIGRATE_REPO = os.path.join(dbdir, "db_repository")
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # TASK_DIR = os.path.join(basedir, "tasks")
    # CRON_LOG = os.path.join(basedir, "cron.log")

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    WEB_HOOK_URL = os.environ.get("TELEGRAM_WEB_HOOK")
    ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
    REDIS_URL = os.environ.get("REDIS_URL")

    LOGGING = {
        "version": 1,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "telegram": {
                "class": "telegram_handler.HtmlFormatter",
                "fmt": "<code>%(asctime)s</code> <b>%(levelname)s</b>\n\nFrom %(name)s:%(funcName)s\n%(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "stream": "ext://sys.stderr",
            },
            # "cron_file": {
            #     "class": "logging.FileHandler",
            #     "level": "INFO",
            #     "formatter": "simple",
            #     "filename": CRON_LOG,
            # },
            # "telegram": {
            #     "class": "telegram_handler.TelegramHandler",
            #     "token": "308111857:AAHTegbywKr36GQN7VCoQ29m2-ry2Wgc14A",
            #     "chat_id": "227756922",
            #     "level": "ERROR",
            #     "formatter": "telegram",
            # },
        },
        "loggers": {
            # "fb_events": {"handlers": ["telegram"], "propagate": "no"},
            # "fb_events.cron": {"handlers": ["cron_file"], "propagate": "no"},
        },
        "root": {"level": "WARNING", "handlers": ["stderr"]},
    }
    DEFAULT_QUIZ = os.path.join(basedir, "data/quiz.json")
    DISTANSE_ERROR = 10


class ProductionConfig(Config):
    """Production configuration."""

    DEVELOPMENT = False
    SELF_SIGNED_SSL = True
    LOG = Config.LOGGING
    LOG.update({"root": {"level": "WARNING", "handlers": ["stderr"]}})


class DevelopmentConfig(Config):
    """Development configuration."""

    DEVELOPMENT = True
    SELF_SIGNED_SSL = True
    LOG = Config.LOGGING
    LOG.update({"root": {"level": "DEBUG", "handlers": ["console"]}})
    WEB_HOOK_URL = "https://gmedbot.pagekite.me/"
    REDIS_URL = "redis://127.0.0.1:6379/0"
