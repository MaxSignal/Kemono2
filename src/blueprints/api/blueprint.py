from flask import Blueprint, request, make_response, jsonify

from src.blueprints.api.v1.types import TDAPIResponseFailure

from .legacy import legacy_api
from .v1 import v1api

api = Blueprint('api', __name__, url_prefix="/api")


@api.before_request
def is_json():
    if (request.method == "GET" or request.is_json):
        return

    api_response = TDAPIResponseFailure(
        is_successful=False,
        errors=["Request is not of JSON type."]
    )

    return make_response(jsonify(api_response), 400)


api.register_blueprint(legacy_api)
api.register_blueprint(v1api)
