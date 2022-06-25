import mock
import jwt
from werkzeug.security import generate_password_hash

import api.tools as tools
from db.db import Users
from app import app


def test_jwtBelongsAdmin_passAdminPassword_returnTrue():
    with app.test_request_context():
        # Password from config.API_PASS
        assert tools.jwt_belongs_admin(
            {'admin_password': 'X+0080CSWvqaf4csZI0vtbbMk1E='})


def test_jwtBelongsAdmin_passInvalidAdminPassword_returnTrue():
    with app.test_request_context():
        assert not tools.jwt_belongs_admin({'admin_password': 'wrong'})


def test_jwtBelongsAdmin_doNotPassAdminPassword_returnFalse():
    with app.test_request_context():
        assert not tools.jwt_belongs_admin({})


def test_getJwt_passValidEncodedData_returnRawData():
    raw_data = {
        'admin_password': 'X+0080CSWvqaf4csZI0vtbbMk1E=',
        'email': 'fakeuser123@gmail.com',
        'password': '123456'
    }
    token = jwt.encode(
        raw_data,
        'sfajiuwtr8qwe04tdgjvrwi90gh0a8090ergvb8wr0r9vecxb92r783cr78',
        algorithm='HS256'
    )
    request_mock = mock.MagicMock()
    request_mock.headers = {'Authorization': f'Bearer {token}'}
    with mock.patch("api.tools.request", request_mock):
        with app.test_request_context():
            assert tools.get_jwt() == raw_data


def test_getJwt_passNonDictData_returnEmptyDict():
    random_token = 'hf4879fhchd3rhdiajopohwqpsfdoe5vq'
    request_mock = mock.MagicMock()
    request_mock.headers = {'Authorization': f'Bearer {random_token}'}
    with mock.patch("api.tools.request", request_mock):
        with app.test_request_context():
            assert tools.get_jwt() == {}


def test_getJwt_passInvalidAdminPass_returnEmptyDict():
    raw_data = {
        'admin_password': 'lgdlgmka;fcoci4fom i4x3cx3',
    }
    token = jwt.encode(
        raw_data,
        'sfajiuwtr8qwe04tdgjvrwi90gh0a8090ergvb8wr0r9vecxb92r783cr78',
        algorithm='HS256'
    )
    request_mock = mock.MagicMock()
    request_mock.headers = {'Authorization': f'Bearer {token}'}
    with mock.patch("api.tools.request", request_mock):
        with app.test_request_context():
            assert tools.get_jwt() == {}
