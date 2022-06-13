import math

from flask import Blueprint, jsonify, make_response, redirect, request, url_for

auth_api = Blueprint('auth', __name__, url_prefix='/auth')


@auth_api.post("/login")
def login_account():
    """"""
