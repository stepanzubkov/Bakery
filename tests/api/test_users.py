from tools import request_with_jwt


def test_getUsers_withoutLimit_returnAllUsers():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/users', method='get')
    assert response.json()['items_count'] == response.json()['total']


def test_getUsers_withLimit_returnFewUsers():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/users?start=3&end=6', method='get')

    assert response.json()['items_count'] <= response.json()['total']


def test_getUsers_withSort_returnSortedUsers():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/users?sort=email', method='get')

    for indx, elem in enumerate(response.json()['items']):
        assert elem['email'] >= response.json(
        )['items'][indx-1 if indx > 0 else 0]['email']


def test_getUsers_withFilter_returnFilteredUsers():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/users?filter=is_verified', method='get')

    for elem in response.json()['items']:
        assert elem['is_verified']
