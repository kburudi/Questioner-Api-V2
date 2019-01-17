""" contains all endpoints for user functions such as signup and login """

import os
import datetime
import jwt
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from ..utils.base_vals import BaseValidation
from ..utils.user_vals import UserValidation
from ..models.user import User
v2_blue = Blueprint("ap1v2", __name__)
KEY = os.getenv("SECRET")


@v2_blue.route("/signup", methods=["POST"])
def user_signup():
    """ endpoint for user to create account """
    try:
        user_data = request.get_json()
        valid_user = UserValidation(user_data)
        valid_user.check_missing_fields(valid_user.signup_required)
        firstname = user_data["firstname"]
        lastname = user_data["lastname"]
        othername = user_data["othername"]
        phone = user_data["phone"]
        email = user_data["email"]
        username = user_data["username"]
        password = user_data["password"]
        valid_user.check_field_values_no_whitespace(valid_user.signup_required)
        valid_user.valid_username()
        valid_user.validate_email()
        valid_user.validate_password()
        valid_user.validate_phone()
        valid_user.validate_names()
        username_taken = User.query_username(username)
        if username_taken:
            return jsonify({"status": 409, "error": "user with username exists"}), 409
        new_user = User(firstname, lastname, othername, username, email,
                        phone, password)
        new_user.create_new_user()
    except TypeError:
        return jsonify({"status": 417, "error": "Expecting signup data!!"}), 417

    return jsonify({"status": 201, "message": "user created successfully"}), 201


@v2_blue.route("/all", methods=["GET"])
def all_users():
    all_of = User.get_all_users()
    return jsonify(all_of)


@v2_blue.route("/login", methods=['POST'])
def user_login():
    """ endpoint for users to sign in """
    try:
        log_data = request.get_json()

    except TypeError:
        return jsonify({"status": 417, "error": "Expecting Login data!!"}), 417

    valid_login = UserValidation(log_data)
    valid_login.check_missing_fields(["username", "password"])
    valid_login.check_field_values_no_whitespace(["username", "password"])
    username = log_data["username"]
    password = log_data["password"]
    user_found = User.query_username(username)
    if not user_found:
        return jsonify({"status": 401, "error": "unregistered username"}), 401
    if not check_password_hash(user_found[0][-1], password):
        return jsonify({"status": 401, "error": "incorrect password"}), 401

    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    token = jwt.encode(
        {"username": username, 'exp': exp}, KEY,
        algorithm='HS256')

    return jsonify({"status": 200, "message": "logged in successfully",
                    "token": token.decode("utf-8", KEY)}), 200
