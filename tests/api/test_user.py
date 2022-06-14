from tools import request_with_jwt


def test_getUser_sendValidAuthtorization_returnOk():
    response = request_with_jwt(
        url='http://localhost:5000/api/v1/user', method='get')

    assert response.status_code == 200
