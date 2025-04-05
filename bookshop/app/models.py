# This is where the database models and queries will go.

from flask_login import UserMixin
from . import mysql

class User(UserMixin):
    def __init__(self, id, full_name, email, password_hash, is_admin):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin

def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if user:
        return User(*user)
    return None
