import os

from tools import request_with_jwt


def test_getProduct_sendValidRequest_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product', method='get')

    assert response.status_code == 200


def test_deleteProduct_sendValidRequest_deleteProductAndReturnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product', method='delete')

    assert response.status_code == 200
    assert response.json()['status'] == 'Successfuly'


def test_putProduct_doNotSendData_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product', method='put')

    assert response.status_code == 200


def test_putProducts_sendInvalidData_returnRequestError():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product', method='put', data={
            'name': 2.11,
            'price': 'Croissant',
            'description': 'Something'
        })

    assert response.status_code == 400
    assert response.json()[0]['type'] == 'type_error.float'


def test_putProduct_sendValidData_returnChangedProduct():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product', method='put', data={
            'name': 'Test product 2',
            'price': 2.99,
            'description': 'Something'
        })

    assert response.status_code == 200
    assert response.json()['name'] == 'Test product 2'
    assert response.json()['price'] == 2.99
    assert response.json()['description'] == 'Something'


def test_putProduct_sendImageWithoutData_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product', method='put', data={
            'image': ''
        })

    assert response.status_code == 200


def test_putProduct_sendNotImage_returnValueError():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product 2', method='put',
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
        url='http://localhost:5000/api/v1/products/Test product 2', method='put',
        files={
            'image': open(os.path.dirname(__file__) + '/test copy.jpg', 'rb')
        })

    assert response.status_code == 200
    assert 'test_copy.jpg' in response.json(
    )['_embedded']['image']['_links']['self']
