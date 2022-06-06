import jwt
from requests import request, Response


def request_with_jwt(*args, **kwargs) -> Response:
    token = jwt.encode(
        {
            "admin_password": 'X+0080CSWvqaf4csZI0vtbbMk1E=',
            'email': 'stepanzubkov2009@gmail.com',
            'password': '123456'
        },
        'sfajiuwtr8qwe04tdgjvrwi90gh0a8090ergvb8wr0r9vecxb92r783cr78',
        algorithm='HS256'
    )
    return request(*args, **kwargs, headers={
        'Authorization': f'Bearer {token}'
    })
