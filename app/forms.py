from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, HiddenField
from wtforms.validators import InputRequired


class BallotForm(FlaskForm):
    nomineesHidden = HiddenField('NomineesHidden')


class LoginForm(FlaskForm):
    username = TextField('Username', [InputRequired('The Username field is required.')])
    password = PasswordField('Password', [InputRequired('The Password field is required.')])

