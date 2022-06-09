from flask import current_app, request, jsonify, Blueprint, g

import os
from werkzeug.utils import secure_filename

from db.db import Products, Reviews
from .tools import (get_jwt, get_request_errors,
                    get_user_from_token,
                    sorted_products, sorted_reviews, sorted_orders,
                    add_to_db, get_borders, delete_product)
from .models import (OrderModel, ProductModel, ErrorModel,
                     PostProduct, PutProduct, ReviewModel,
                     PostBaseReview)


api = Blueprint("api", __name__)

PICTURES = '/app/pictures'


@api.before_request
def before_request():
    token_data = get_jwt()

    if not token_data:
        return jsonify([
            ErrorModel(
                source='token',
                type='value_error.missing',
                description=('value is not '
                             'specified, expired or contains wrong data')
            ).dict()
        ]), 403

    g.user = get_user_from_token(token_data)


@api.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = sorted_products()
        start_border, end_border = get_borders(products)

        items = [
            ProductModel.create(product, request).dict(
                by_alias=True, exclude_unset=True
            )
            for product in products[start_border:end_border]
        ]

        return jsonify(total=len(products),
                       items_count=len(items), items=items)

    elif request.method == 'POST':
        image = request.files.get('image')
        errors = get_request_errors(PostProduct, image)
        if errors:
            return jsonify(errors), 400

        product = Products(
            name=request.form['name'],
            price=float(request.form['price']),
            description=request.form.get('description')
        )
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(PICTURES, filename))
            product.image_url = f'/pictures/{filename}'

        db_error = add_to_db(product)
        if db_error:
            return db_error

        item = ProductModel.create(product, request)
        return jsonify(item.dict(by_alias=True, exclude_unset=True))


@api.route('/products/<name>', methods=['GET', 'DELETE', 'PUT'])
def single_product(name):
    product = Products.query.filter_by(name=name).first_or_404()

    if request.method == 'GET':
        item = ProductModel.create(product, request)
        return jsonify(item.dict(
            by_alias=True, exclude_unset=True
        ))

    elif request.method == 'DELETE':
        delete_product(product)

        return jsonify(
            status='Successfuly'
        )

    elif request.method == 'PUT':
        image = request.files.get('image')
        errors = get_request_errors(PutProduct, image)
        if errors:
            return jsonify(errors), 400

        for k, v in request.form.items():
            setattr(product, k, v)

        if image:
            old_image_url = product.image_url

            filename = secure_filename(image.filename)
            image.save(os.path.join(PICTURES, filename))
            product.image_url = f'/pictures/{filename}'

            (not old_image_url.startswith('/static')
             and os.remove(current_app.instance_path + old_image_url))

        db_error = add_to_db(product)
        if db_error:
            return db_error

        item = ProductModel.create(product, request)
        return jsonify(item.dict(by_alias=True, exclude_unset=True))


@api.route('/products/<name>/reviews', methods=['GET', 'POST'])
def product_reviews(name):
    product = Products.query.filter_by(name=name).first_or_404()

    if request.method == 'GET':
        reviews = sorted_reviews(product.reviews)
        start_border, end_border = get_borders(reviews)

        items = [
            ReviewModel.create(review, request).dict(
                by_alias=True, exclude_unset=True
            )
            for review in reviews[start_border:end_border]
        ]

        return jsonify(total=len(reviews),
                       items_count=len(items), items=items)

    elif request.method == 'POST':

        if g.get('user'):
            image = request.files.get('image')
            errors = get_request_errors(PostBaseReview, image)
            if errors:
                return jsonify(errors), 400

            review = Reviews(
                owner_id=g.user.id,
                product_id=product.id,
                text=request.form.get('text'),
                rating=request.form['rating']
            )
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(PICTURES, filename))
                review.image_url = f'/pictures/{filename}'

            db_error = add_to_db(review)
            if db_error:
                return db_error

            item = ReviewModel.create(review, request)
            return jsonify(item.dict(by_alias=True, exclude_unset=True))
        else:
            return jsonify([
                ErrorModel(
                    source='token',
                    type='value_error.missing_user_data',
                    description='value doesn\'t contain user data'
                ).dict()
            ]), 400


@api.route('/products/<name>/orders', methods=['GET'])
def product_orders(name):
    product = Products.query.filter_by(name=name).first_or_404()

    orders = sorted_orders(product.orders)
    start_border, end_border = get_borders(orders)

    items = [
        OrderModel.create(order, request).dict(
            by_alias=True, exclude_unset=True
        )
        for order in orders[start_border:end_border]
    ]

    return jsonify(total=len(orders), items_count=len(items),
                   items=items)
