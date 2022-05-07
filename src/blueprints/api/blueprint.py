from flask import Blueprint

from .legacy import legacy_api
from .v1 import v1api

api = Blueprint('api', __name__, url_prefix="/api")

api.register_blueprint(legacy_api)
api.register_blueprint(v1api)
