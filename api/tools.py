from flask import current_app, request, jsonify

import os
import jwt
from typing import Type
from pydantic import BaseModel, ValidationError
from werkzeug.datastructures import FileStorage
from werkzeug.security import check_password_hash as check_hash

from .models import ErrorModel
from db.db import Users, Products, Reviews, Orders, db


def jwt_belongs_admin(decoded_token: str) -> bool:
    return (
        decoded_token.get('admin_password', '') ==
        current_app.config['API_PASS']
    )


def get_jwt() -> dict:
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        data = jwt.decode(
            token, current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
    except jwt.exceptions.DecodeError:
        return {}

    if jwt_belongs_admin(data):
        return data
    else:
        return {}


def get_user_from_token(data: dict) -> Users:
    email = data.get('email', '')
    password = data.get('password', '')

    user = Users.query.filter_by(email=email).first()
    if user and check_hash(user.password, password):
        return user


def is_allowed(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    if ext[1:] in ['png', 'jpg']:
        return True
    return False


def validate_image(image: FileStorage) -> list:
    if image and not is_allowed(image.filename):
        return [
            ErrorModel(
                source='image',
                type='type_error.image',
                description=('extension is not allowed.'
                             ' Please upload only .png or .jpg files.')
            ).dict()
        ]

    else:
        return []


def validate_request_body(model: Type[BaseModel]) -> list:
    try:
        model(**request.form)
    except ValidationError as errors:

        errors = errors.errors()
        for e in errors:
            custom_errors = []
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


def get_request_errors(model: Type[BaseModel], image: FileStorage) -> list:
    return validate_request_body(model) + validate_image(image)


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


def sorted_products() -> list:
    sort_type = request.args.get('sort', '')

    if sort_type == 'desc_price':
        products = Products.query.order_by(Products.price.desc())
    elif sort_type == 'asc_price':
        products = Products.query.order_by(Products.price)
    elif sort_type == 'popular':
        products = Products.query.order_by(Products.sales.desc())
    elif sort_type == 'alphabet':
        products = Products.query.order_by(Products.name)
    else:
        products = Products.query

    return products.all()


def sorted_reviews(reviews) -> list:
    sort_type = request.args.get('sort')

    if sort_type == 'asc_rating':
        reviews = reviews.order_by(Reviews.rating)
    elif sort_type == 'desc_rating':
        reviews = reviews.order_by(Reviews.rating.desc())

    return reviews.all()


def sorted_orders(orders) -> list:
    sort_type = request.args.get('sort')

    if sort_type == 'asc_date':
        orders = orders.order_by(Orders.created_at)
    elif sort_type == 'desc_date':
        orders = orders.order_by(Orders.created_at.desc())

    return orders.all()


def get_borders(elements):
    start = (int(request.args.get('start', ''))-1
             if request.args.get('start', '').isdigit() else 0)
    end = (int(request.args.get('end', ''))
           if request.args.get('end', '').isdigit() else len(elements))

    return (start, end)


def add_to_db(*args):
    try:
        for obj in args:
            db.session.add(obj)
        db.session.commit()
    except Exception as e:
        return handle_error(e), 500


def delete_product(product):
    try:
        Reviews.query.filter_by(
            product_id=product.id).delete(synchronize_session=False)
        Orders.query.filter_by(
            product_id=product.id).delete(synchronize_session=False)
        db.session.delete(product)
        db.session.commit()
    except Exception as e:
        return handle_error(e), 400
