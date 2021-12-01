import os
from typing import List, Optional


class ENV_VARS:
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    ARCHIVER_HOST = os.getenv('ARCHIVERHOST')
    ARCHIVER_PORT = os.getenv('ARCHIVERPORT', '8000')


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
