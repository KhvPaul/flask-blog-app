from flask_security.forms import RegisterForm, LoginForm
from wtforms import StringField, validators, PasswordField, BooleanField


class SignUpForm(RegisterForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])




