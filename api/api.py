from flask import Blueprint
from db.db import Users
import jwt
from flask import current_app, request, jsonify


api = Blueprint("api", __name__)


def check_jwt(token: str) -> bool:
    """Check jwt token and return boolean

    Args:
        token (str): token to check
    """
    try:
        data = jwt.decode(
            token, current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )

        assert data['password'] == current_app.config['API_PASS']

    except Exception:
        return False
    return True


@api.before_request
def before_request():
    if not check_jwt(request.args.get('token', '')):
        return jsonify(
            source='token',
            type='MISSING_JWT_TOKEN',
            message=('JWT Authentication token is not '
                     'specified, expired or contains wrong data'),
        ), 403
