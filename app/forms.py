from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, HiddenField
from wtforms.validators import InputRequired


class BallotForm(FlaskForm):
    nomineesHidden = HiddenField('NomineesHidden')


class LoginForm(FlaskForm):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])

