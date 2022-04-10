from flask_login import LoginManager

from db import Users
from user import User

manager = LoginManager()


@manager.user_loader
def load_user(id):
    return User().fromDB(int(id), Users)
