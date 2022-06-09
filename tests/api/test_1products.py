import os
import requests

from tools import request_with_jwt


def test_beforeRequest_dontSendJwt_returnForbiddenError():
    response = requests.get('http://localhost:5000/api/v1/products')

    assert response.status_code == 403


def test_beforeRequest_sendValidJwt_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products', method='get')
    assert response.status_code == 200


def test_getProducts_withoutLimit_returnAllProducts():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products', method='get')
    assert response.json()['items_count'] == response.json()['total']


def test_getProducts_withLimit_returnFewProducts():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products?start=3&end=6', method='get')

    assert response.json()['items_count'] == 4


def test_getProducts_withSort_returnSortedProducts():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products?sort=desc_price', method='get')

    for indx, elem in enumerate(response.json()['items']):
        assert elem['price'] <= response.json(
        )['items'][indx-1 if indx > 0 else 0]['price']


def test_postProduct_doNotSendData_returnRequestErrors():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products', method='post')

    assert response.status_code == 400


def test_postProducts_doNotSendImage_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products', method='post', data={
            'name': 'Test product',
            'price': 2.11
        })

    assert response.status_code == 200
    assert '/static/images/notfound.png' in response.json(
    )['_embedded']['image']['_links']['self']


def test_postProducts_sendImageWithoutData_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products', method='post', data={
            'name': 'Test product',
            'price': 2.11,
            'image': ''
        })

    assert response.status_code == 200
    assert '/static/images/notfound.png' in response.json(
    )['_embedded']['image']['_links']['self']


def test_postProduct_sendNotImage_returnValueError():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products', method='post',
        data={
            'name': 'Test product 2',
            'price': 2.11
        },
        files={
            'image': open(os.path.dirname(__file__) + '/test.epub', 'rb').read()
        })

    assert response.status_code == 400
    assert response.json()[0]['type'] == 'type_error.image'


def test_postProduct_sendValidImage_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products', method='post',
        data={
            'name': 'Test product 2',
            'price': 2.11
        },
        files={
            'image': open(os.path.dirname(__file__) + '/test.jpg', 'rb')
        })

    assert response.status_code == 200
    assert 'test.jpg' in response.json(
    )['_embedded']['image']['_links']['self']
