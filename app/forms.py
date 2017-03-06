from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import DataRequired

class BallotForm(FlaskForm):
    nomineesHidden = HiddenField('nomineesHidden')

class LoginForm(FlaskForm):
    uname = StringField('uname', validators=[DataRequired()])
    passwd = PasswordField('passwd', validators=[DataRequired()])

