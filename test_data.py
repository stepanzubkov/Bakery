from app import db, app, Products

with app.test_request_context():
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
        ['Tortilla', 2.49, 19]
    ]
    for pr in products:
        db.session.add(Products(name=pr[0], price=pr[1], sales=pr[2]))
    db.session.commit()
