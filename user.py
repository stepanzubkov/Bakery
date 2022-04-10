from flask_login import UserMixin


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
