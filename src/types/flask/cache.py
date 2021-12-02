from typing import List, Protocol


class FLASK_CACHE_CONFIG(Protocol):
    """
    The flask config keys used by `flask_caching`.
    """
    CACHE_DEFAULT_TIMEOUT: int = 300
    CACHE_IGNORE_ERRORS: bool = False
    CACHE_THRESHOLD: int = 500
    CACHE_KEY_PREFIX: str = "flask_cache_"
    CACHE_MEMCACHED_SERVERS: None
    CACHE_DIR: None
    CACHE_OPTIONS: None
    CACHE_ARGS: List = []
    CACHE_TYPE: str = "null"
    CACHE_NO_NULL_WARNING: bool = False
    CACHE_SOURCE_CHECK: bool = False
