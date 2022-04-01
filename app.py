from flask import Flask
from db import db, migrate, Products

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
migrate.init_app(app, db)


@app.route('/', methods=['GET'])
def index():
    return 'Hello, Docker!'
