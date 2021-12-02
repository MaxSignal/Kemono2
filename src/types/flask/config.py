from datetime import timedelta
from typing import Protocol


class FLASK_CONFIG(Protocol):
    """
    https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.default_config
    """
    APPLICATION_ROOT: str = '/'
    DEBUG: None
    ENV: None
    EXPLAIN_TEMPLATE_LOADING: bool = False
    JSONIFY_MIMETYPE: str = 'application/json'
    JSONIFY_PRETTYPRINT_REGULAR: bool = False
    JSON_AS_ASCII: bool = True
    JSON_SORT_KEYS: bool = True
    MAX_CONTENT_LENGTH: None
    MAX_COOKIE_SIZE: int = 4093
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(days=31)
    PREFERRED_URL_SCHEME: str = 'http'
    PRESERVE_CONTEXT_ON_EXCEPTION: None
    PROPAGATE_EXCEPTIONS: None
    SECRET_KEY: None
    SEND_FILE_MAX_AGE_DEFAULT: None
    SERVER_NAME: None
    SESSION_COOKIE_DOMAIN: None
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_NAME: str = 'session'
    SESSION_COOKIE_PATH: None
    SESSION_COOKIE_SAMESITE: None
    SESSION_COOKIE_SECURE: bool = False
    SESSION_REFRESH_EACH_REQUEST: True
    TEMPLATES_AUTO_RELOAD: None
    TESTING: bool = False
    TRAP_BAD_REQUEST_ERRORS: None
    TRAP_HTTP_EXCEPTIONS: bool = False
    USE_X_SENDFILE: bool = False
