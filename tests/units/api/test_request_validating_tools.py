from unittest.mock import MagicMock
from werkzeug.datastructures import FileStorage
import mock
import os

from api.models import ReviewModel
import api.tools as tools


def test_isAllowed_passPngFilename_returnTrue():
    assert tools.is_allowed('smth.png')


def test_isAllowed_passJpgFilename_returnTrue():
    assert tools.is_allowed('smth.jpg')


def test_isAllowed_passTxtFilename_returnFalse():
    assert not tools.is_allowed('smth.txt')


def test_isAllowed_passPdfFilename_returnFalse():
    assert not tools.is_allowed('smth.pdf')


def test_isAllowed_passNonFilename_returnFalse():
    assert not tools.is_allowed('Lorem ipsum dolar sit amet')


def test_validateImage_passValidFileStorage_returnEmptyList():
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'test_files/valid_image.jpg')

    with open(file_path, 'rb') as f:
        file_storage = FileStorage(f)

    assert tools.validate_image(file_storage) == []


def test_validateImage_passInvalidFileStorage_returnErrorList():
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'test_files/invalid_image.txt')

    with open(file_path, 'rb') as f:
        file_storage = FileStorage(f)

    assert isinstance(tools.validate_image(file_storage)[0], dict)


def test_validateImage_passNone_returnEmptyList():
    assert tools.validate_image(None) == []


def test_validateRequestBody_passValidRequest_returnEmptyList():
    request_mock = MagicMock()
    request_mock.form = {
        'text': 'Some',
        'rating': 3,
        '_links': {'smth': {'smth': 'smth'}}
    }

    with mock.patch('api.tools.request', request_mock):
        assert tools.validate_request_body(ReviewModel) == []


def test_validateRequestBody_passInvalidRequest_returnErrorList():
    request_mock = MagicMock()
    request_mock.form = {
        'rating': 'lorem ipsum dolar sit amet',
        '_links': 4
    }

    with mock.patch('api.tools.request', request_mock):
        result = tools.validate_request_body(ReviewModel)
        assert result != []
        for i in result:
            assert isinstance(i, dict)


def test_validateRequestBody_doNotPassRequest_returnErrorList():
    request_mock = MagicMock()
    request_mock.form = {}
    with mock.patch('api.tools.request', request_mock):
        result = tools.validate_request_body(ReviewModel)
        assert result != []
        for i in result:
            assert isinstance(i, dict)


def test_validateRequestBody_passValidRequest_returnEmptyList():
    request_mock = MagicMock()
    request_mock.form = {
        'text': 'Some',
        'rating': 3,
        '_links': {'smth': {'smth': 'smth'}}
    }

    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'test_files/valid_image.jpg')

    with open(file_path, 'rb') as f:
        file_storage = FileStorage(f)

    with mock.patch('api.tools.request', request_mock):
        assert tools.get_request_errors(ReviewModel, file_storage) == []
