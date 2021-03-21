import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from .config import config

"""APP creation and configuration"""

swagger = Swagger()
migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config['dev'])
    app.config['REQUESTS_ORIGIN'] = os.getenv('REQUESTS_ORIGIN')
    app.config['TOKEN_NAME'] = 'X-Token'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    login_manager.login_view = "login"
    login_manager.session_protection = "strong"
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    swagger.init_app(app)

    with app.app_context():
        db.create_all()

    return app
