from flask_login import UserMixin
from flask import current_app

from time import time
import jwt


class User(UserMixin):
    def fromDB(self, user_id, users):
        self.user = users.query.get(user_id)
        return self

    def create(self, user):
        self.user = user
        return self

    def get_id(self):
        if self.user is not None:
            return self.user.id
        else:
            return 0

    @staticmethod
    def generate_access_key(email: str, expires: int = 600) -> str:
        """Generate access key to send it to user's email

        Args:
            email (str): email, used to encode
            expires (int, optional): Key expiration date
                                     from now in seconds. Defaults to 600.

        Returns:
            str: Access key
        """
        return jwt.encode(
            {"access_email": email, "exp": time() + expires},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def check_access_key(key: str) -> bool | str:
        """Check access key

        Args:
            key (str): Access key to check

        Returns:
            bool | str: email, if access key is valid,
                        else False
        """
        try:
            email = jwt.decode(key, current_app.config['SECRET_KEY'],
                               algorithms=['HS256'])['access_email']
        except Exception:
            return False
        return email
