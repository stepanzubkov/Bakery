from flask import Request, current_app, request, jsonify

import jwt
import os
from typing import Type
from pydantic import BaseModel, ValidationError
from werkzeug.security import check_password_hash as check_hash
from werkzeug.datastructures import FileStorage

from .models import ErrorModel
from db.db import Users, db


def is_allowed(filename: str) -> bool:
    """Check image extension and return boolean

    Args:
        filename (str): name of file

    Returns:
        bool: filename is valid image (png or jpg)
    """
    _, ext = os.path.splitext(filename.lower())
    if ext[1:] in ['png', 'jpg']:
        return True
    return False


def jwt_belongs_admin(decoded_token: str) -> bool:
    """Check the decoded_token contains right admin password

    Args:
        encoded_token (str): jwt token data

    Returns:
        bool: decoded_token belongs admin
    """
    return (
        decoded_token.get('admin_password', '') ==
        current_app.config['API_PASS']
    )


def get_jwt() -> None | dict:
    """Gets jwt token data from 'Authorization: Bearer ...' header

        Returns:
            dict | None: token data
    """
    token = request.headers.get('Authorization').replace('Bearer ', '')
    data = jwt.decode(
        token, current_app.config['SECRET_KEY'],
        algorithms=['HS256']
    )

    if jwt_belongs_admin(data):
        return data


def get_user_from_token(data: dict) -> Users:
    email = data.get('email', '')
    password = data.get('password', '')

    user = Users.query.filter_by(email=email).first()
    if user and check_hash(user.password, password):
        return user


def check_image(image: FileStorage) -> dict | None:
    """Check image and return error

    Args:
        image (FileStorage): image to check

    Returns:
        dict | None: error data
    """
    if image and not is_allowed(image.filename):
        return ErrorModel(
            source='image',
            type='type_error.image',
            description=('extension is not allowed.'
                         ' Please upload only .png or .jpg files.')
        ).dict()


def validate_request_body(request: Request, model: Type[BaseModel]) -> list:
    try:
        model(**request.form)
    except ValidationError as errors:
        custom_errors = []
        errors = errors.errors()
        for e in errors:
            custom_errors.append(
                ErrorModel(
                    source=e['loc'][0],
                    type=e['type'],
                    description=e['msg']
                ).dict()
            )

        return custom_errors

    else:
        return []


def handle_error(error_message: str) -> None:
    """Writes error_message to logs, rollbacks db and throws an error

    Args:
        error_message (str): message to logs

    Returns:
        None
    """
    current_app.logger.error(error_message)

    db.session.rollback()
    return jsonify([
        ErrorModel(
            source='server',
            type='server_error.database',
            description='Error with the database.'
        ).dict()
    ])
