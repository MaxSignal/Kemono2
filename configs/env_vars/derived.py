from distutils.util import strtobool
from .vars import ENV_VARS


class DERIVED_VARS:
    IS_DEVELOPMENT = ENV_VARS.FLASK_ENV == 'development'
    ARCHIVER_ORIGIN = f'http://{ENV_VARS.ARCHIVER_HOST}:{ENV_VARS.ARCHIVER_PORT}'
    IS_PASSWORD_VALIDATION = strtobool(
        str(ENV_VARS.ENABLE_PASSWORD_VALIDATOR)
    )
    IS_LOGIN_RATE_LIMITED = strtobool(
        str(ENV_VARS.ENABLE_LOGIN_RATE_LIMITING)
    )
