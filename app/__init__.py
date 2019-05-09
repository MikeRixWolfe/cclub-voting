from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_pyfile('app.cfg')

app.url_map.strict_slashes = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app import auth, vote
app.register_blueprint(auth.bp)
app.register_blueprint(vote.bp)

db.create_all()
