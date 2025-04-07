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
