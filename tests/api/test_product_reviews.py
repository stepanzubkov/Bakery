import os
import jwt
from requests import request

from tools import request_with_jwt


def test_getProductReviews_withoutLimit_returnAllReviews():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/reviews', method='get')

    assert response.json()['items_count'] == response.json()['total']


def test_getProductReviews_withLimit_returnFewReviews():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/reviews?start=2&end=6', method='get')

    assert response.json()['items_count'] <= response.json()['total']


def test_getProductReviews_withSort_returnSortedReviews():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/reviews?sort=desc_rating', method='get')

    for indx, elem in enumerate(response.json()['items']):
        assert elem['rating'] <= response.json(
        )['items'][indx-1 if indx > 0 else 0]['rating']


def test_postProductReviews_doNotSendUserData_returnRequestError():
    token = jwt.encode(
        {
            "admin_password": 'X+0080CSWvqaf4csZI0vtbbMk1E='
        },
        'sfajiuwtr8qwe04tdgjvrwi90gh0a8090ergvb8wr0r9vecxb92r783cr78',
        algorithm='HS256'
    )
    response = request(
        url='http://localhost:5000/api/v1/products/Test product/reviews',
        method='post',
        headers={
            'Authorization': f'Bearer {token}'
        })

    assert response.status_code == 400
    assert response.json()[0]['type'] == 'value_error.missing_user_data'


def test_postProductReviews_doNotSendData_returnRequestErrors():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/reviews', method='post')

    assert response.status_code == 400
    assert len(response.json()) == 1
    assert response.json()[0]['type'] == 'value_error.missing'


def test_postProductReviews_doNotSendImage_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/reviews', method='post', data={
            'rating': 2,
            'text': 'Test review'
        })

    assert response.status_code == 200


def test_postProductReviews_sendImageWithoutData_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/reviews', method='post', data={
            'rating': 2,
            'text': 'Test review',
            'image': ''
        })

    assert response.status_code == 200


def test_postProductReviews_sendNotImage_returnValueError():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/reviews', method='post',
        data={
            'rating': 4,
            'text': 'Test review'
        },
        files={
            'image': open(os.path.dirname(__file__) + '/test.epub', 'rb').read()
        })

    assert response.status_code == 400
    assert response.json()[0]['type'] == 'type_error.image'


def test_postProductReviews_sendValidImage_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/reviews', method='post',
        data={
            'rating': 5,
            'text': 'Test review'
        },
        files={
            'image': open(os.path.dirname(__file__) + '/test.jpg', 'rb')
        })

    assert response.status_code == 200
    assert 'test.jpg' in response.json(
    )['_embedded']['image']['_links']['self']
