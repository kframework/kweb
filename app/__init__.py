from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import shutil, os
from config import BASE_DIR, SESSION_LIFETIME
from werkzeug.local import LocalProxy
from datetime import timedelta

# Setup Flask
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# Setup flask-loginmanager
lm = LoginManager()
lm.setup_app(app)
lm.login_view = "login"

app.permanent_session_lifetime = timedelta(days=SESSION_LIFETIME)

# Start app
from app import views, models
