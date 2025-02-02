from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
import redis
from config import Config

# Create the Flask app instance
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config.Config')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Set the login view for Flask-Login

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=app.config['CACHE_REDIS_HOST'],
    port=app.config['CACHE_REDIS_PORT'],
    db=app.config['CACHE_REDIS_DB']
)

# Initialize Flask-Caching with Redis
cache = Cache(app, config={
    'CACHE_TYPE': app.config['CACHE_TYPE'],
    'CACHE_REDIS': redis_client
})

# Import routes after initializing app and extensions
from routes import *
