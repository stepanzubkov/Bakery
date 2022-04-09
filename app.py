from flask import Flask, render_template, send_from_directory, flash
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash as gen_hash
# from werkzeug.security import check_password_hash as check_hash

import os
from base64 import b64encode
from threading import Thread

from forms import RegistrationForm
from db import db, migrate, Products, Users


app = Flask(__name__)
app.config.from_pyfile('config.py')


mail = Mail(app)
db.init_app(app)
migrate.init_app(app, db)


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject, recipient, template, **kwargs):
    msg = Message(
        subject, sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
    return thr


@app.route('/', methods=['GET'])
def index():
    # Most popular products
    products = Products.query.order_by(Products.sales.desc()).all()
    return render_template('index.html', products=products, title='Home')


@app.route('/pictures/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        users_emails = [u.email for u in Users.query.all()]
        if form.email.data in users_emails:
            flash('Account with this email already exists', category='error')
            return render_template('registration.html', title='Registration',
                                   form=form)
        try:
            access_key = b64encode(os.urandom(50)).decode(
                'utf-8').replace('/', '')
            user = Users(first_name=form.first_name.data,
                         last_name=form.last_name.data,
                         email=form.email.data,
                         password=gen_hash(form.password.data),
                         address=form.address.data,
                         access_key=access_key
                         )
            db.session.add(user)
            db.session.commit()

            send_mail(subject="Confirmation from Bakery",
                      recipient=form.email.data,
                      template='mail.html',
                      name=f'{form.first_name.data} {form.last_name.data}',
                      key=access_key, id=user.id)
            flash('You have received a confirmation email', category='success')
        except Exception as e:
            print(f'ERROR WHILE ADDING USER: {e}')
            flash('Something went wrong', category='error')
            db.session.rollback()

    return render_template('registration.html', title='Registration',
                           form=form)


@app.route('/confirm/<int:id>/<key>', methods=['GET'])
def confirm(id, key):
    user = Users.query.get(id)
    if user.access_key == key:
        try:
            user.is_verified = True
            db.session.add(user)
            db.session.commit()
            return "Success!"
        except Exception as e:
            print(f'ERROR WHILE CONFIRM EMAIL: {e}')
            db.session.rollback()

    else:
        return "Wrong key"
