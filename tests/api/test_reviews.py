from tools import request_with_jwt


def test_getReviews_withoutLimit_returnAllReviews():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/reviews', method='get')

    assert response.json()['items_count'] == response.json()['total']


def test_getReviews_withLimit_returnFewReviews():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/reviews?start=2&end=6', method='get')

    assert response.json()['items_count'] <= response.json()['total']


def test_getReviews_withSort_returnSortedReviews():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/reviews?sort=desc_rating', method='get')

    for indx, elem in enumerate(response.json()['items']):
        assert elem['rating'] <= response.json(
        )['items'][indx-1 if indx > 0 else 0]['rating']
