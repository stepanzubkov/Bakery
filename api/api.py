from flask import current_app, request, jsonify, Blueprint, g

import os
from werkzeug.utils import secure_filename

from db.db import Products, Reviews, Orders, db
from .tools import (check_image, get_jwt,
                    get_user_from_token, handle_error,
                    sorted_products, validate_request_body)
from .models import (OrderModel, ProductModel, ErrorModel,
                     PostProduct, PutProduct, ReviewModel,
                     PostBaseReview)


api = Blueprint("api", __name__)


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
        # Limit borders
        start = (int(request.args.get('start', ''))
                 if request.args.get('start', '').isdigit() else 1)
        end = (int(request.args.get('end', ''))
               if request.args.get('end', '').isdigit() else len(products))

        items = []
        for product in products[start-1:end]:
            item = ProductModel.create(product, request)
            items.append(item.dict(by_alias=True, exclude_unset=True))

        return jsonify(total=len(products),
                       items_count=len(items), items=items)

    elif request.method == 'POST':
        custom_errors = validate_request_body(request, PostProduct)

        image = request.files.get('image')

        # If user specified image field, but not load file
        if image and not image.filename:
            image = None

        image_error = check_image(image)
        image_error and custom_errors.append(image_error)

        if custom_errors:
            return jsonify(custom_errors), 400

        name = request.form['name']
        description = request.form.get('description')
        price = float(request.form['price'])

        try:
            product = Products(name=name, price=price,
                               description=description)
            if image:
                filename = secure_filename(image.filename)
                pictures = os.path.join(current_app.instance_path, 'pictures')
                image.save(os.path.join(pictures, filename))
                product.image_url = f'/pictures/{filename}'

            db.session.add(product)
            db.session.commit()
        except Exception as e:
            return handle_error(e), 500

        item = ProductModel.create(product, request)

        return jsonify(item.dict(by_alias=True, exclude_unset=True))


@api.route('/products/<name>', methods=['GET', 'DELETE', 'PUT'])
def single_product(name):
    product = Products.query.filter_by(name=name).first_or_404()

    if request.method == 'GET':
        item = ProductModel.create(product, request)
        return jsonify(item.dict())

    elif request.method == 'DELETE':
        try:
            Reviews.query.filter_by(
                product_id=product.id).delete(synchronize_session=False)
            Orders.query.filter_by(
                product_id=product.id).delete(synchronize_session=False)
            db.session.delete(product)
            db.session.commit()
        except Exception as e:
            return handle_error(e), 400

        return jsonify(
            status='Successfuly'
        )

    elif request.method == 'PUT':
        custom_errors = validate_request_body(request, PutProduct)

        # If user specified image field, but not load file
        image = request.files.get('image')
        if image and not image.filename:
            image = None

        image_error = check_image(image)
        image_error and custom_errors.append(image_error)

        if custom_errors:
            return jsonify(custom_errors), 400

        try:
            for k in request.form:
                if request.form[k]:
                    setattr(product, k, request.form[k])

            if image:
                old_image_url = product.image_url
                filename = secure_filename(image.filename)
                pictures = os.path.join(current_app.instance_path, 'pictures')
                image.save(os.path.join(pictures, filename))
                product.image_url = f'/pictures/{filename}'
                ('/static/images/notfound.png' != old_image_url
                 and os.remove(current_app.instance_path + old_image_url))

            db.session.add(product)
            db.session.commit()

        except Exception as e:
            return handle_error(e), 500

        item = ProductModel.create(product, request)
        return jsonify(item.dict(by_alias=True, exclude_unset=True))


@api.route('/products/<name>/reviews', methods=['GET', 'POST'])
def product_reviews(name):
    product = Products.query.filter_by(name=name).first_or_404()

    if request.method == 'GET':
        reviews = product.reviews

        sort_type = request.args.get('sort')
        if sort_type == 'asc_rating':
            reviews = reviews.order_by(Reviews.rating)
        elif sort_type == 'desc_rating':
            reviews = reviews.order_by(Reviews.rating.desc())

        reviews = reviews.all()

        # Limit borders
        start = (int(request.args.get('start', ''))
                 if request.args.get('start', '').isdigit() else 1)
        end = (int(request.args.get('end', ''))
               if request.args.get('end', '').isdigit() else len(reviews))

        items = []
        for review in reviews[start-1:end]:
            item = ReviewModel.create(review, request)
            items.append(item.dict(by_alias=True, exclude_unset=True))

        return jsonify(total=len(reviews),
                       items_count=len(items), items=items)

    elif request.method == 'POST':

        if g.get('user'):
            custom_errors = validate_request_body(request, PostBaseReview)

            image = request.files.get('image')

            if image and not image.filename:
                image = None

            image_error = check_image(image)
            image_error and custom_errors.append(image_error)

            if custom_errors:
                return jsonify(custom_errors), 400

            try:
                review = Reviews(
                    owner_id=g.user.id,
                    product_id=product.id,
                    text=request.form.get('text'),
                    rating=request.form['rating']
                )

                if image:
                    filename = secure_filename(image.filename)
                    pictures = os.path.join(
                        current_app.instance_path, 'pictures')
                    image.save(os.path.join(pictures, filename))
                    review.image_url = f'/pictures/{filename}'

                db.session.add(review)
                db.session.commit()
            except Exception as e:
                return handle_error(e), 500

            else:
                return jsonify(ReviewModel.create(review, request)
                               .dict(by_alias=True, exclude_unset=True))
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

    orders = product.orders

    sort_type = request.args.get('sort')
    if sort_type == 'asc_date':
        orders = orders.order_by(Orders.created_at)
    elif sort_type == 'desc_date':
        orders = orders.order_by(Orders.created_at.desc())
    orders = orders.all()

    # Limit borders
    start = (int(request.args.get('start', ''))
             if request.args.get('start', '').isdigit() else 1)
    end = (int(request.args.get('end', ''))
           if request.args.get('end', '').isdigit() else len(orders))

    items = []
    for order in orders[start-1:end]:
        items.append(
            OrderModel.create(request, order).dict(
                by_alias=True, exclude_unset=True)
        )

    return jsonify(total=len(orders), items_count=len(items),
                   items=items)
