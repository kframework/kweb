from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import shutil, os
from config import BASE_DIR
from werkzeug.local import LocalProxy

# Setup Flask
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# Setup flask-loginmanager
lm = LoginManager()
lm.setup_app(app)
lm.login_view = "login"

# Start app
from app import views, models
