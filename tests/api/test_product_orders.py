from datetime import datetime

from tools import request_with_jwt


def test_getProductOrders_withoutLimit_returnAllOrders():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/orders', method='get')

    assert response.json()['items_count'] == response.json()['total']


def test_getProductOrders_withLimit_returnFewOrders():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/orders?start=2&end=6', method='get')

    assert response.json()['items_count'] <= response.json()['total']


def test_getProductOrders_withSort_returnSortedOrders():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/products/Test product/orders?sort=desc_date', method='get')

    for indx, elem in enumerate(response.json()['items']):
        assert (
            datetime.fromisoformat(elem['created_at_utc']) <=
            datetime.fromisoformat(
                response.json()
                ['items']
                [indx-1 if indx > 0 else 0]
                ['created_at_utc']
            )
        )
