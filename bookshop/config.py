import os

SECRET_KEY = os.urandom(24)
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:rootroot@localhost/bookshop_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
