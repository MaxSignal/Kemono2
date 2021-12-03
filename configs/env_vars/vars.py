import os
from typing import List, Optional

from dotenv import load_dotenv

from .constants import CONSTANTS

kemono_env_values = ['production', 'development']

# TODO: use it later
env_filename = dict(
    development='.env.dev',
    production='.env.prod'
)

load_dotenv(CONSTANTS.PROJECT_PATH.joinpath('.env'))


class ENV_VARS:
    FLASK_ENV = os.getenv('FLASK_ENV')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    FLASK_CACHE_TYPE = os.getenv('FLASK_CACHE_TYPE')
    FLASK_CACHE_DEFAULT_TIMEOUT = os.getenv('FLASK_CACHE_DEFAULT_TIMEOUT')
    ARCHIVER_HOST = os.getenv('KEMONO_ARCHIVER_HOST')
    ARCHIVER_PORT = os.getenv('KEMONO_ARCHIVER_PORT')
    DATABASE_HOST = os.getenv('DATABASE_HOST')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    DATABASE_USER = os.getenv('DATABASE_USER')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
    DATABASE_PORT = os.getenv('DATABASE_PORT')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    KEMONO_SITE = os.getenv('KEMONO_SITE')
    ENABLE_PASSWORD_VALIDATOR = os.getenv('KEMONO_ENABLE_PASSWORD_VALIDATOR')
    ENABLE_LOGIN_RATE_LIMITING = os.getenv('KEMONO_ENABLE_LOGIN_RATE_LIMITING')
    UPLOAD_LIMIT = os.getenv('KEMONO_UPLOAD_LIMIT')
    REQUEST_IMAGES = os.getenv('KEMONO_REQUESTS_IMAGES')
    PROXIES = os.getenv('KEMONO_PROXIES')
    BAN_URL = os.getenv('KEMONO_BAN_URL')
    PUBKEY = os.getenv('KEMONO_PUBKEY')
    SALT = os.getenv('KEMONO_SALT')
    PUBSUB = os.getenv('KEMONO_PUBSUB')
    PUBSUB_QUEUE_LIMIT = os.getenv('KEMONO_PUBSUB_QUEUE_LIMIT')
    TELEGRAM_TOKEN = os.getenv('KEMONO_TELEGRAM_TOKEN')
    TELEGRAM_CHANNEL = os.getenv('KEMONO_TELEGRAM_CHANNEL')


# print("\n".join(["Environment Variables: \n"
#     f"{attr}:{value}"
#     for attr, value
#     in ENV_VARS.__dict__.items()
# ]))


def validate_vars(var_list: List[Optional[str]]):
    missing_vars = []

    for var in var_list:
        if not getattr(ENV_VARS, var, None):
            missing_vars.append(var)

    if missing_vars:
        var_string = ", ".join(missing_vars)
        raise ValueError(f'These environment variables are not set: {var_string}')


critical_vars = []
validate_vars(critical_vars)
