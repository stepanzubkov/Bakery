from flask import Flask, render_template, send_from_directory
from db import db, migrate, Products

app = Flask(__name__)
app.config.from_pyfile('config.py')


db.init_app(app)
migrate.init_app(app, db)


@app.route('/', methods=['GET'])
def index():
    products = Products.query.order_by(Products.sales.desc()).all()
    return render_template('index.html', products=products, title='Home')


@app.route('/pictures/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
