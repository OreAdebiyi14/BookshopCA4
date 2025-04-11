from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.user_id)

class Book(db.Model):
    __tablename__ = 'Books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    publisher = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2))
    category = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
    image_url = db.Column(db.String(255))
    stock_quantity = db.Column(db.Integer)
    description = db.Column(db.Text)
    reviews = db.relationship('Review', backref='book', cascade='all, delete-orphan')

class CartItem(db.Model):
    __tablename__ = 'CartItems'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('Books.book_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship('User', backref='cart_items')
    book = db.relationship('Book')

class Order(db.Model):
    __tablename__ = 'Orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    address_id = db.Column(db.Integer, db.ForeignKey('Addresses.address_id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('Payments.payment_id'))
    order_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    total_price = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50))

    user = db.relationship('User', backref='orders')
    items = db.relationship('Item', backref='order', cascade='all, delete-orphan')

    @property
    def total(self):
        return sum(item.price_at_purchase * item.quantity for item in self.items)

class Item(db.Model):
    __tablename__ = 'Items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('Books.book_id'))
    quantity = db.Column(db.Integer)
    price_at_purchase = db.Column(db.Numeric(10, 2))

    book = db.relationship('Book')

class Review(db.Model):
    __tablename__ = 'Reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('Books.book_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User')

class Address(db.Model):
    __tablename__ = 'Addresses'
    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    street = db.Column(db.String(255))
    city = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

    user = db.relationship('User', backref='addresses')

class Payment(db.Model):
    __tablename__ = 'Payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    card_number = db.Column(db.String(20))
    expiry_date = db.Column(db.String(10))
    cvv = db.Column(db.String(4))

    user = db.relationship('User', backref='payments')
