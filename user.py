from flask_login import UserMixin
from flask import current_app
from db import Users
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
    def generate_access_key(email, expires=600) -> str:
        return jwt.encode(
            {"access_email": email, "exp": time() + expires},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def check_access_key(key) -> bool | str:
        try:
            email = jwt.decode(key, current_app.config['SECRET_KEY'],
                               algorithms=['HS256'])['access_email']
        except:
            return False
        return email
