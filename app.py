from user import User
from login import manager
from db import Reviews, db, migrate, Products, Users, Orders
from forms import (
    RegistrationForm, LoginForm, SettingsForm,
    EmailChangeForm, PasswordChangeForm, SortForm,
    ReviewForm, BuyForm
)
from threading import Thread
import os
from datetime import datetime

from cloudipsp import Api, Checkout
import requests
from werkzeug.security import (
    check_password_hash as check_hash,
    generate_password_hash as gen_hash,
)
from werkzeug.utils import secure_filename
from flask_login import (
    login_required, login_user, current_user,
    logout_user
)
from flask_mail import Mail, Message
from flask import (
    Flask, render_template, send_from_directory,
    flash, request, redirect
)

app = Flask(__name__, instance_path='/app')
app.config.from_pyfile('config.py')

folder = os.path.join(app.instance_path, 'pictures')

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
        users_emails = [u.email for u in Users.query.all() if u.is_verified]
        if form.email.data in users_emails:
            flash('Account with this email already exists', category='error')
            return render_template('registration.html', title='Registration',
                                   form=form)
        try:

            access_key = User.generate_access_key(form.email.data)

            user = Users(first_name=form.first_name.data,
                         last_name=form.last_name.data,
                         email=form.email.data,
                         password=gen_hash(form.password.data),
                         address=form.address.data
                         )
            db.session.add(user)
            db.session.commit()

            send_mail(subject="Confirmation from Bakery",
                      recipient=form.email.data,
                      template='mail.html',
                      name=f'{form.first_name.data} {form.last_name.data}',
                      key=access_key)
            flash('You have received a confirmation email', category='success')
        except Exception as e:
            app.logger.error(f'ERROR WHILE ADDING USER: {e}')
            flash('Something went wrong', category='error')
            db.session.rollback()

    return render_template('registration.html', title='Registration',
                           form=form)


@app.route('/confirm/registration/<key>', methods=['GET'])
def confirm_registration(key):
    email = User.check_access_key(key)
    if email:
        try:
            user = Users.query.filter_by(email=email).first()
            user.is_verified = True

            db.session.add(user)
            db.session.commit()

            userlogin = User().create(user)
            login_user(userlogin, remember=True)
            return redirect('/profile')
        except Exception as e:
            app.logger.error(f'ERROR WHILE CONFIRM EMAIL: {e}')
            db.session.rollback()
            return "Something went wrong"

    else:
        return "Wrong key or key is expired"


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
    return render_template('profile.html', title='Profile', user=user,
                           reviews_count=len(user.reviews.all()))


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
            app.logger.error(f'ERROR WHILE EDITING SETTINGS: {e}')
            flash('Something went wrong', category='error')
            db.session.rollback()
    return render_template('profile_settings.html', title='Settings',
                           user=user, form=form, getattr=getattr)


@app.route('/change/password/step1', methods=['GET'])
@login_required
def change_password_1():
    user = Users.query.get(current_user.get_id())
    send_mail(subject="Confirmation from Bakery",
                      recipient=user.email,
                      template='change_password_mail.html',
                      name=f'{user.first_name} {user.last_name}',
                      key=user.access_key, id=user.id)
    return render_template('password_change_1.html', title='Step 1')


@app.route('/change/password/step2/<key>', methods=['GET', 'POST'])
@login_required
def change_password_2(key):
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
                app.logger.error(f'ERROR WHILE CHANGE PASSWORD: {e}')
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
    return render_template('email_change.html', title='Change email',
                           form=form)


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
            app.logger.error(f'ERROR WHILE CONFIRM EMAIL: {e}')
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
    page = int(page) if str(page).isdigit() else 1

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

    reviews = Reviews.query.order_by(Reviews.id.desc()).limit(10).all()
    return render_template('menu.html', title='Menu', page=pages[page-1],
                           form=form, pages_count=len(pages),
                           nav_pages=nav_pages, current_page=page,
                           reviews=reviews)


@app.route('/products/<name>', methods=['GET'])
def product(name):
    product = Products.query.filter_by(name=name).first_or_404()
    summary_rating = (
        sum([r.rating for r in product.reviews]) /
        len(product.reviews.all())) \
        if product.reviews.all() \
        else 0.0
    summary_rating = round(summary_rating, 1)
    return render_template('product.html', title=product.name,
                           reviews_count=len(product.reviews.all()),
                           product=product, summary_rating=summary_rating)


@app.route('/products/<name>/buy', methods=['GET', 'POST'])
@login_required
def product_buy(name):
    form = BuyForm()
    product = Products.query.filter_by(name=name).first_or_404()
    if form.validate_on_submit():
        try:
            user = Users.query.get(current_user.get_id())
            address = form.address.data \
                if form.address_choose.data == 'custom' \
                else user.address

            order = Orders(
                product_id=product.id,
                owner_id=user.id,
                address=address,
                wishes=form.wishes.data,
            )

            db.session.add(order)
            db.session.commit()

            api = Api(merchant_id=1396424,
                      secret_key='test')
            checkout = Checkout(api=api)
            data = {
                "currency": "USD",
                "amount": int(product.price*100),
                "response_url": f"http://localhost:5000/order-accept/{order.id}/{user.access_key}"
            }

            url = checkout.url(data).get('checkout_url')
            return redirect(url)
        except Exception as e:
            app.logger.error(f'ERROR WHILE ADD ORDER: {e}')
            db.session.rollback()
            flash("Something went wrong")

    return render_template('buy.html', title='Order', product=product,
                           form=form)


@ app.route('/products/<name>/review', methods=['GET', 'POST'])
@login_required
def review(name):
    product = Products.query.filter_by(name=name).first_or_404()
    form = ReviewForm()
    if form.validate_on_submit():
        try:
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                form.image.data.save(os.path.join(folder, filename))

            review = Reviews(
                text=form.text.data,
                rating=form.rating.data,
                product_id=product.id,
                owner_id=current_user.get_id(),
                image_url='/pictures/'+filename if form.image.data else None
            )

            db.session.add(review)
            db.session.commit()

            return redirect(f'/products/{product.name}')
        except Exception as e:
            app.logger.error(f'ERROR WHILE CREATE REVIEW: {e}')
            flash('Something went wrong', category='error')
            db.session.rollback()
    return render_template('review.html', title='Review', form=form,
                           product=product)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html', title='Contact us')


@app.route('/blog', methods=['GET'])
def blog():
    '''
    This page will work without youtube access token,
    but videos will not be shown.
    For this feature, create google apis
    application and create file
    youtube_token.txt with you access token
    '''
    owner_id = '-212903410'  # VK community id
    access_token = '997587369975873699758736389909ddf59997599758736fb12194e34710227d78e44b9'  # public token
    vk_posts = requests.get(
        f"http://api.vk.com/method/wall.get?owner_id={owner_id}&v=5.131&access_token={access_token}&count=10")
    posts = [
        {
            "image": post["attachments"][0]["photo"]["sizes"][6]["url"]
            if post.get("attachments") else None,
            "text":
                post["text"][:200] + ('...' if len(post["text"]) > 150 else '')
                if post.get('attachments') else
                post['text'],
            "link": f"https://vk.com/wall{owner_id}_{post['id']}",
            "date": datetime.fromtimestamp(int(post['date'])).isoformat()
        }
        for post in vk_posts.json()["response"]["items"]
    ]

    try:
        with open('youtube_token.txt', 'r') as f:
            youtube_key = f.read()
            channel_id = 'UCgnXl05I8AcM-XmnxBvKL3w'
    except FileNotFoundError:
        videos = []
        return render_template('blog.html', title='Blog', posts=posts, videos=videos)

    channel = requests.get(
        f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={youtube_key}').json()
    playlist_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    playlist = requests.get(
        f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=20&playlistId={playlist_id}&key={youtube_key}').json()

    videos = [
        {
            "name": video['snippet']['title'],
            "image": video['snippet']['thumbnails']['medium']['url'],
            "url": f'https://www.youtube.com/watch?v={video["snippet"]["resourceId"]["videoId"]}'

        }
        for video in playlist['items']
    ]
    return render_template('blog.html', title='Blog', posts=posts, videos=videos)


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', title='About us')


@app.route('/order-accept/<int:id>/<key>', methods=['GET', 'POST'])
def order_accept(id, key):
    order = Orders.query.filter_by(id=id).first_or_404()
    user = Users.query.filter_by(
        id=order.owner_id,
        access_key=key
    ).first_or_404()

    try:
        order.status = 'accepted'

        db.session.add(order)
        db.session.commit()
    except Exception as e:
        app.logger.error(f'ERROR WHILE ACCEPT ORDER: {e}')
        db.session.rollback()
        flash("Something went wrong")

    return redirect('/profile')
