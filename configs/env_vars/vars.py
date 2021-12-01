import os
from typing import List, Optional

from dotenv import load_dotenv

from .constants import CONSTANTS

load_dotenv(CONSTANTS.PROJECT_PATH.joinpath('.env'))


class ENV_VARS:
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    ARCHIVER_HOST = os.getenv('ARCHIVERHOST')
    ARCHIVER_PORT = os.getenv('ARCHIVERPORT', '8000')
    KEMONO_SITE = os.getenv('KEMONO_SITE')
    REQUEST_IMAGES = os.getenv('REQUESTS_IMAGES', '1048576')
    PGHOST = os.getenv('PGHOST'),
    PGDATABASE = os.getenv('PGDATABASE'),
    PGUSER = os.getenv('PGUSER'),
    PGPASSWORD = os.getenv('PGPASSWORD'),
    PGPORT = os.getenv('PGPORT', '5432'),
    TELEGRAMTOKEN = os.getenv('TELEGRAMTOKEN')
    TELEGRAMCHANNEL = os.getenv('TELEGRAMCHANNEL')
    UPLOAD_LIMIT = os.getenv('UPLOAD_LIMIT')


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
