from tools import request_with_jwt


def test_getUserOrders_sendValidAuthtorization_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/user/orders', method='get')

    assert response.status_code == 200
