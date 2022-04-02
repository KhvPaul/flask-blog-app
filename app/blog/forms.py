from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField
from wtforms import validators


class BlogForm(FlaskForm):
    content_style = {'style': 'min-height: 25vh;'}

    title = StringField('Title: ', validators=[validators.DataRequired(), validators.Length(1, 200)])
    content = TextAreaField('Content:', validators=[validators.DataRequired()], render_kw=content_style)
    publication_request = BooleanField('Request publication: ', default=False)


class CommentForm(FlaskForm):
    author = StringField('Author:')
    content = TextAreaField('Content:')


class ContactUsForm(FlaskForm):
    email = StringField('Email:', validators=[validators.DataRequired(), validators.Email()])
    content = TextAreaField('Content:', validators=[validators.DataRequired()])
