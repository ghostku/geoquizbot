import os


class Config(object):
    # Определяет включен ли режим отладки
    DEBUG = False

    # Включение защиты против "Cross-site Request Forgery (CSRF)"
    CSRF_ENABLED = True

    # Случайный ключ, которые будет исползоваться для подписи
    # данных, например cookies.
    SECRET_KEY = 'FSdf4f444D4443sd_!5GSD'

    basedir = os.path.abspath(os.path.dirname(__file__))
    dbdir = os.path.join(basedir, 'data/db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(dbdir, 'gbot.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(dbdir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TASK_DIR = os.path.join(basedir, 'tasks')
    CRON_LOG = os.path.join(basedir, 'cron.log')
    # TELEGRAM_BOT_TOKEN = '308111857:AAHTegbywKr36GQN7VCoQ29m2-ry2Wgc14A'
    LOGGING = {
        'version': 1,
        'formatters': {
            'simple': {
                'format':
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'telegram': {
                'class':
                'telegram_handler.HtmlFormatter',
                'fmt':
                '<code>%(asctime)s</code> <b>%(levelname)s</b>\n\nFrom %(name)s:%(funcName)s\n%(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'stderr': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': 'ext://sys.stderr'
            },
            'cron_file': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'filename': CRON_LOG
            },
            'telegram': {
                'class': 'telegram_handler.TelegramHandler',
                'token': '308111857:AAHTegbywKr36GQN7VCoQ29m2-ry2Wgc14A',
                'chat_id': '227756922',
                'level': 'ERROR',
                'formatter': 'telegram'
            }
        },
        'loggers': {
            'fb_events': {
                'handlers': ['telegram'],
                'propagate': 'no'
            },
            'fb_events.cron': {
                'handlers': ['cron_file'],
                'propagate': 'no'
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['stderr']
        }
    }
    TELEBOT_WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше
    # TODO: Переписать формирование URL с кусокв через urlparse
    MESSAGES = {
        'stats':
        '**Статистика по работам:**\nВсего: {}\nДолжны: {} UAH\nЗаработано всего: {} UAH\nОценка открытых проектов: {} UAH\n\nПо статусам:\n{}',
        'record':
        '__{name}__\n\nПоследнее изменение:{last_updated}\nКоментарий: {comment}\n'
    }
    RECORD_STATUSES = ['Work', 'Done', 'Fail', 'Wait', 'Call']
    LAST_SET_HOOK_TRY = ''


class ProductionConfig(Config):
    DEVELOPMENT = False
    SELF_SIGNED_SSL = True
    LOG = Config.LOGGING
    LOG.update({'root': {'level': 'WARNING', 'handlers': ['stderr']}})
    TELEBOT_TOKEN = '517477451:AAHlSgvG0J6J_Af9jsqJnBWIKSk3jm8pK5Q'
    TELEBOT_WEBHOOK_HOST = 'bot.ghostku.com'
    TELEBOT_WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
    TELEBOT_WEBHOOK_PATH = "/bot/%s/" % TELEBOT_TOKEN
    TELEBOT_WEBHOOK_SSL_CERT = '/etc/self/cert.pem'  # Путь к сертификату
    GSRY_URL = 'https://script.google.com/macros/s/AKfycbz7RrFDk63hZWsazCRGlRnUoOwl06kt1MNIg_W47oobJ3-d5n6-/exec'
    # REDIS_URL = 'redis://redis_db:6379/0'
    REDIS_URL = os.environ.get("REDIS_URL")


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    SELF_SIGNED_SSL = True
    LOG = Config.LOGGING
    LOG.update({'root': {'level': 'DEBUG', 'handlers': ['console']}})
    TELEBOT_TOKEN = '604331438:AAEAdPDMb9nt7RAh7kpsLArADAV88GNyHw4'
    TELEBOT_WEBHOOK_HOST = 'devbot.ghostku.com'
    TELEBOT_WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
    TELEBOT_WEBHOOK_PATH = "/bot/%s" % TELEBOT_TOKEN
    TELEBOT_WEBHOOK_SSL_CERT = './dev/gbot_dev_cert.pem'  # Путь к сертификату
    TELEBOT_WEBHOOK_SSL_PRIV = './dev/gbot_dev_pkey.pem'  # Путь к приватному ключу
    GSRY_URL = 'https://script.google.com/macros/s/AKfycbxXEw8wForVFGM8dMdZrwI_Lfmk4s76mYAaeh2dpIvz7PL8faD8/exec'
    REDIS_URL = 'redis://127.0.0.1:6379/0'