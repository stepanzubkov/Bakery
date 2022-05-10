from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData

convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s'
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    sales = db.Column(db.Integer, default=0, nullable=False)
    image_url = db.Column(
        db.String(100), default='/pictures/notfound.png', nullable=False)
    reviews = db.relationship('Reviews', backref='product', lazy='dynamic',
                              uselist=True)
    orders = db.relationship(
        'Orders', backref='product', lazy='dynamic', uselist=True)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100))
    reviews = db.relationship(
        'Reviews', backref='owner', lazy='dynamic', uselist=True)
    orders = db.relationship(
        'Orders', backref='owner', lazy='dynamic', uselist=True)


class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                         nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           nullable=False)
    text = db.Column(db.Text)
    rating = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(100))


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                         nullable=False)
    address = db.Column(db.String(100), nullable=False)
    wishes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    status = db.Column(db.String(50), default='created')

    @property
    def created(self):
        return str(self.created_at)[:19]

    @created.setter
    def created(self, value):
        self.created_at = value
