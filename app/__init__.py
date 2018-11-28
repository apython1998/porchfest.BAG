from flask import Flask
from flask_mongoengine import MongoEngine
from config import Config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
db = MongoEngine(app)
login = LoginManager(app)
login.login_view = 'logIn'
bootstrap = Bootstrap(app)

from app import routes, models
