# config.py

import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ABD0001256')
    SESSION_COOKIE_NAME = 'ABD_session'

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:1@localhost/school')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cache settings
    CACHE_TIMEOUT = 10  # Cache timeout in seconds

    # Redis settings for Flask-Caching
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0

    # Other settings (add more as needed)
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
