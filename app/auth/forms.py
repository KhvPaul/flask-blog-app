from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, EmailField
from wtforms.validators import ValidationError, StopValidation
from wtforms import validators

from flask_security import current_user
from flask_security.utils import hash_password, verify_password

from app.models import Blogger


def email_exist(form, field):
    if not Blogger.query.filter(Blogger.email == field.data).first():
        raise StopValidation('Unknown identifier')


def email_available(form, field):
    if Blogger.query.filter(Blogger.email == field.data).first():
        raise ValidationError('Email exist, use another')


def username_available(form, field):
    if Blogger.query.filter(Blogger.username == field.data).first():
        raise ValidationError(f'Username is taken. U can use {field.data}1, {field.data}11, {field.data}123')


def password_correct(form, field):
    data, email = str(form.email).split(), ''
    for el in data:
        if 'value=' in el:
            email = el.split('"')[1]
    blogger = Blogger.query.filter(Blogger.email == email).first()
    if blogger:
        if not verify_password(field.data, blogger.password):
            raise ValidationError('Wrong password')


def check_password_before_change(form, field):
    if not verify_password(field.data, current_user.password):
        raise ValidationError('Wrong password')


class SignUpForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25), username_available])
    email = EmailField('Email Address', [validators.Length(min=6, max=35), validators.Email(), email_available])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=6),
        validators.EqualTo('password_confirm')
    ])
    password_confirm = PasswordField('Repeat Password')


class SingInForm(FlaskForm):
    email = EmailField('Email', validators=[validators.DataRequired(), validators.Length(1, 64), email_exist])
    password = PasswordField('Password', validators=[validators.DataRequired(), password_correct])
    remember = BooleanField('Keep me logged in')


class ChangePasswordCheckForm(FlaskForm):
    password = PasswordField('Previous password', validators=[validators.DataRequired(), check_password_before_change])


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=6),
        validators.EqualTo('password_confirm')
    ])
    password_confirm = PasswordField('Repeat Password')


class ResetPasswordForm(FlaskForm):
    pass


class BloggerForm(FlaskForm):
    first_name = StringField('First name:', validators=[validators.Length(0, 50)])
    last_name = StringField('Last name:', validators=[validators.Length(0, 50)])
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()])
    phone = StringField('Phone:', validators=[validators.Length(0, 15)])
    address = StringField('Adress:', validators=[validators.Length(0, 50)])
    bio = TextAreaField('Biography')
    # picture =
