from os import getenv
DEBUG = True
SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
