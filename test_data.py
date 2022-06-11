from werkzeug.security import generate_password_hash

from app import db, app, Products, Users, Reviews, Orders

with app.test_request_context():
    db.create_all()
    products = [
        ['Croissant', 1.49, 0],
        ['Bagel', 0.99, 129],
        ['White bread', 3.49, 44],
        ['Rye bread', 3.99, 11],
        ['Cake', 14.99, 3],
        ['Donut', 2.49, 178],
        ['Roll', 0.89, 12],
        ['Crisp bread', 1.59, 21],
        ['Coffee', 3.99, 206],
        ['Green tea', 2.99, 18],
        ['Black tea', 2.99, 12],
        ['Pita bread', 3.09, 78],
        ['Tortilla', 2.49, 19],
        ['Test product', 2.99, 32]
    ]

    reviews = [
        [1, 4, 'Tasty!!! Delicious!!!', 5, '/pictures/r.jpg'],
        [1, 1, 'Tasty!!! Delicious!!!', 3, '/pictures/r.jpg'],
        [1, 2, 'Tasty!!! Delicious!!!', 0, '/pictures/r.jpg'],
        [1, 3, 'Tasty!!! Delicious!!!', 2, '/pictures/r.jpg'],
        [1, 4, 'Tasty!!! Delicious!!!', 1, '/pictures/r.jpg'],
        [1, 4, 'Tasty!!! Delicious!!!', 4, '/pictures/r.jpg'],
        [1, 4, 'Tasty!!! Delicious!!!', 5, '/pictures/r.jpg'],
        [1, 4, 'Tasty!!! Delicious!!!', 5, '/pictures/r.jpg'],
        [1, 4, 'Tasty!!! Delicious!!!', 5, '/pictures/r.jpg'],
        [1, 4, 'Tasty!!! Delicious!!!', 5, '/pictures/r.jpg'],
        [1, 5, 'Tasty!!! Delicious!!!', 5, '/pictures/r.jpg'],
        [1, 5, 'Tasty!!! Delicious!!!', 0, '/pictures/r.jpg'],
        [1, 5, 'Tasty!!! Delicious!!!', 0, '/pictures/r.jpg'],
        [1, 5, 'Tasty!!! De1icious!!!', 0, '/pictures/r.jpg'],
        [1, 5, 'Tasty!!! Delicious!!!', 0, '/pictures/r.jpg'],
        [1, 5, 'Tasty!!! Delicious!!!', 2, '/pictures/r.jpg'],
        [1, 14, 'Tasty!!! Delicious!!!', 3, '/pictures/r.jpg'],
        [1, 14, 'Tasty!!! Delicious!!!', 5, '/pictures/r.jpg'],
        [1, 14, 'Tasty!!! Delicious!!!', 5, '/pictures/r.jpg'],
        [1, 14, 'Tasty!!! Delicious!!!', 2, '/pictures/r.jpg']
    ]

    orders = [
        [1, 14, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 14, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 14, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 14, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 14, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 14, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 14, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 14, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 1, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 12, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 11, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 11, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 11, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 11, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 11, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some'],
        [1, 11, 'Fake Republic, New Null, Non-Existent St., 92, 12 flat', 'Some']
    ]

    for pr in products:
        db.session.add(Products(name=pr[0], price=pr[1], sales=pr[2]))

    db.session.add(Users(
        email='fakeuser123@gmail.com',
        password=generate_password_hash('123456'),
        is_verified=True,
        first_name='Fake',
        last_name='Fakery',
        address='Fake Republic, New Null, Non-Existent St., 92, 12 flat'

    ))

    for rv in reviews:
        db.session.add(Reviews(owner_id=rv[0],
                               product_id=rv[1],
                               text=rv[2],
                               rating=rv[3],
                               image_url=rv[4]
                               )
                       )

    for order in orders:
        db.session.add(Orders(owner_id=order[0],
                              product_id=order[1],
                              address=order[2],
                              wishes=order[3]
                              )
                       )
    db.session.commit()
