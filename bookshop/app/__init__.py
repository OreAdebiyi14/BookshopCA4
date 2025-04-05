from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from .models import load_user

mysql = MySQL()
login_manager = LoginManager()
login_manager.user_loader(load_user)

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    mysql.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app
