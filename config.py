from os import getenv
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
UPLOAD_FOLDER = './pictures'
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 mb
SECRET_KEY = 'sfajiuwtr8qwe04tdgjvrwi90gh0a8090ergvb8wr0r9vecxb92r783cr78'

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'carlsbad.bakery@gmail.com'
MAIL_DEFAULT_SENDER = ('Carlsbad Bakery', 'carlsbad.bakery@gmail.com')
MAIL_PASSWORD = 'bakery_carlsbad'

API_PASS = 'X+0080CSWvqaf4csZI0vtbbMk1E='
JSON_SORT_KEYS = False
