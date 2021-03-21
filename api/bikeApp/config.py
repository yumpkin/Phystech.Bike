import os

basedir = os.path.abspath(os.path.dirname(__file__))

"""App Configuration"""


class Auth:
    """Google Project Credentials"""
    CLIENT_ID = '##########SHOULD BE HIDDEN ##########'
    CLIENT_SECRET = '##########SHOULD BE HIDDEN ##########'
    REDIRECT_URI = 'https://localhost:5000/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']


class Config:
    """Base config"""
    APP_NAME = "Bike Zero"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "somethingsecret"


class DevConfig(Config):
    """Dev config"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "test.db")
    AUTHY_API_KEY = '##########SHOULD BE HIDDEN ##########'
    SECRET_KEY = '##########SHOULD BE HIDDEN ##########'


class ProdConfig(Config):
    """Production config"""
    DEBUG = True
    pg_user = "postgres"
    pg_pwd = "38_hYu578"
    pg_port = "5432"
    SQLALCHEMY_DATABASE_URI = "postgresql://{username}:{password}@localhost:{port}/bike_db".format(username=pg_user,
                                                                                                 password=pg_pwd,
                                                                                                 port=pg_port)
    AUTHY_API_KEY = '##########SHOULD BE HIDDEN ##########'
    SECRET_KEY = '##########SHOULD BE HIDDEN ##########'


config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}
