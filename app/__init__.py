from flask import Flask
from flask_mongoengine import MongoEngine
from config import Config
from logging.handlers import RotatingFileHandler
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import os
import logging
from flask_googlemaps import GoogleMaps

app = Flask(__name__)
app.config.from_object(Config)
db = MongoEngine(app)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/porchfest_BAG.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('porchfest_BAG startup')

from app import routes, models, errors
