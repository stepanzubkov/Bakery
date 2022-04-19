from user import User
from login import manager
from db import db, migrate, Products, Users
from forms import (
    RegistrationForm, LoginForm, SettingsForm,
    EmailChangeForm, PasswordChangeForm, SortForm
)
from threading import Thread
from base64 import b64encode
import os
from werkzeug.security import (
    check_password_hash as check_hash,
    generate_password_hash as gen_hash
)
from flask_login import (
    login_required, login_user, current_user,
    logout_user
)
from flask_mail import Mail, Message
from flask import (
    Flask, render_template, send_from_directory,
    flash, request, redirect
)

app = Flask(__name__)
app.config.from_pyfile('config.py')


mail = Mail(app)
manager.init_app(app)
db.init_app(app)
migrate.init_app(app, db)

manager.login_view = 'login'
manager.login_message = 'Sign in to access restricted pages'
manager.login_message_category = 'error'


def without_login(func):
    """Decorator function that redirects the authenticated

    not be visible to the user

    Args:
        func (function): route function
    """
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect('/profile')
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def to_sublists(lst: list, item_count: int = 1) -> list:
    new = []
    while lst:
        new.append(lst[:item_count])
        del lst[:item_count]
    return new


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
@without_login
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
                      key=access_key, id=user.id,
                      remeber=form.remember_me.data)
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

            userlogin = User().create(user)
            login_user(userlogin, remember=eval(request.args.get('remember')))
            return redirect('/profile')
        except Exception as e:
            print(f'ERROR WHILE CONFIRM EMAIL: {e}')
            db.session.rollback()
            return "Something went wrong"

    else:
        return "Wrong key or id"


@app.route('/login', methods=['GET', 'POST'])
@without_login
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if not user or not check_hash(user.password, form.password.data):
            flash('Wrong email or password', category='error')
            return render_template('login.html', title='Sign in', form=form)
        if not user.is_verified:
            flash('Your email is not verified', category='error')
            return render_template('login.html', title='Sign in', form=form)

        if user and check_hash(user.password, form.password.data):
            userlogin = User().create(user)
            login_user(userlogin, remember=form.remember_me.data)
            return redirect('/profile')

    return render_template('login.html', title='Sign in', form=form)


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    user = Users.query.get(current_user.get_id())
    return render_template('profile.html', title='Profile', user=user)


@app.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    form = SettingsForm()
    user = Users.query.get(current_user.get_id())
    if form.validate_on_submit():
        try:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.address = form.address.data

            db.session.add(user)
            db.session.commit()

            return redirect('/profile')
        except Exception as e:
            print(f'ERROR WHILE EDITING SETTINGS: {e}')
            flash('Something went wrong', category='error')
            db.session.rollback()
    return render_template('profile_settings.html', title='Settings',
                           user=user, form=form, getattr=getattr)


@app.route('/change/password/step1', methods=['GET'])
@login_required
def change_email_1():
    user = Users.query.get(current_user.get_id())
    send_mail(subject="Confirmation from Bakery",
                      recipient=user.email,
                      template='change_password_mail.html',
                      name=f'{user.first_name} {user.last_name}',
                      key=user.access_key, id=user.id)
    return render_template('password_change_1.html', title='Step 1')


@app.route('/change/password/step2/<key>', methods=['GET', 'POST'])
@login_required
def method_name(key):
    form = PasswordChangeForm()
    user = Users.query.get(current_user.get_id())
    if user.access_key == key:
        if form.validate_on_submit():
            try:
                user.password = gen_hash(form.password.data)

                db.session.add(user)
                db.session.commit()

                return redirect('/profile')
            except Exception as e:
                print(f'ERROR WHILE CHANGE PASSWORD: {e}')
                flash('Something went wrong', category='error')
                db.session.rollback()
    else:
        return "Wrong key or id"

    return render_template('password_change_2.html', title='Step 2', form=form,
                           key=user.access_key)


@app.route('/profile/email-change', methods=['GET', 'POST'])
@login_required
def email_change():
    user = Users.query.get(current_user.get_id())
    form = EmailChangeForm()
    if form.validate_on_submit():
        send_mail(subject="Confirmation from Bakery",
                  recipient=form.email.data,
                  template='change_email_mail.html',
                  name=f'{user.first_name} {user.last_name}',
                  key=user.access_key, id=user.id, email=form.email.data)
        flash('You have received a confirmation email', category='success')
    return render_template('email_change.html', title='Change email', form=form)


@app.route('/confirm/email/<email>/<key>', methods=['GET'])
@login_required
def confirm_email(key, email):
    user = Users.query.get(current_user.get_id())
    if user.access_key == key:
        try:
            user.email = email
            db.session.add(user)
            db.session.commit()

            return redirect('/profile')
        except Exception as e:
            print(f'ERROR WHILE CONFIRM EMAIL: {e}')
            db.session.rollback()
            return "Something went wrong"

    else:
        return "Wrong key or id"


@app.route('/profile/signout')
@login_required
def signout():
    logout_user()
    return redirect('/')


@app.route('/menu', methods=['GET'])
@login_required
def menu():
    form = SortForm(sort=request.args.get('sort'))
    match request.args.get('sort'):  # Sort products
        case 'desc_price':
            products = Products.query.order_by(Products.price.desc()).all()
        case 'asc_price':
            products = Products.query.order_by(Products.price).all()
        case 'popular':
            products = Products.query.order_by(Products.sales.desc()).all()
        case 'alphabet':
            products = Products.query.order_by(Products.name).all()
        case _:
            products = Products.query.all()

    rows = to_sublists(products, 3)
    pages = to_sublists(rows, 4)

    page = request.args.get('page')
    try:  # Check the page is integer and valid index, else page = 1
        page = int(page)
        pages[page-1]
    except (ValueError, TypeError, IndexError):
        page = 1

    if page == 1:  # First page
        nav_pages = [
            page,
            page+1 if page+1 <= len(pages) else None,
            page+2 if page+2 <= len(pages) else None
        ]
    if page == len(pages):  # Last page
        nav_pages = [
            page-1 if page-1 >= 1 else None,
            page-2 if page-2 <= 1 else None,
            page
        ]
    else:  # Other pages
        nav_pages = [
            page-1, page, page+1
        ]

    return render_template('menu.html', title='Menu', page=pages[page-1],
                           form=form, pages_count=len(pages),
                           nav_pages=nav_pages, current_page=page)
