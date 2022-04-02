from datetime import datetime
from random import randint

from flask import url_for
from flask_security import RoleMixin, UserMixin
from flask_security.utils import hash_password, verify_password

from db import db


def format_date(date):
    if date.day == datetime.now().day:
        return f"{date.strftime('%H:%M:%S')}"
    if date.day == datetime.now().day - 1:
        return f"tomorrow at {date.strftime('%H:%M:%S')}"
    if date.day - datetime.now().day - 1 <= 7:
        return f"{date.day - datetime.now().day}" \
               f" days ago at {date.strftime('%H:%M:%S')}"[1:]
    else:
        return f"{date.strftime('%Y-%m-%d %H:%M:%S')}"


# MTM tables
roles_bloggers_table = db.Table('roles_bloggers',
                                db.Column('blogger_id', db.Integer(), db.ForeignKey('blogger.id')),
                                db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Blogger(db.Model, UserMixin):
    __tablename__ = 'blogger'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_bloggers_table,
                            backref='bloggers', lazy=True)

    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    # file_binary = db.Column(db.BLOB, nullable=True)  # Actual data, needed for Download
    # mimetype = db.Column(db.String(25), nullable=True)

    file_path = db.Column(db.Text, nullable=True, default='auth/images/default_.png')


    blogs = db.relationship('Blog', backref='blogger', passive_deletes=True)

    # blogs = relationship("Blog", back_populates="blogger", cascade="all, delete",
    #                      passive_deletes=True)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password):
        self.password = hash_password(password)

    def check_password(self, password):
        return verify_password(password, self.password)

    def colored_username(self):
        color = ('primary', 'warning', 'info')
        return color[randint(0, 2)]


class Blog(db.Model):
    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.DateTime(), default=datetime.utcnow)
    is_posted = db.Column(db.Boolean, default=False)
    publication_request = db.Column(db.Boolean, default=False)
    notified = db.Column(db.Boolean, default=False)
    route = db.Column(db.String, unique=True)


    blogger_id = db.Column(db.Integer, db.ForeignKey('blogger.id', ondelete="CASCADE"))

    comments = db.relationship('Comment', backref='blog', passive_deletes=True)

    # blogger = db.relationship('Blog', backref=backref('blogs', passive_deletes=True))

    # comments = relationship("Comment", back_populates="blog", cascade="all, delete", passive_deletes=True)

    def __str__(self):
        return f'{self.title}'

    def create_update_route(self, blogger, title):
        title = title.lower()
        route = blogger.username + ':' + str('-'.join(title.split()[0:3]))
        if Blog.query.filter(Blog.route == route).first():
            for i in range(2, 1000):
                if not Blog.query.filter(Blog.route == f'{route}-v{i}').first():
                    route += f'-v{i}'
                    self.title += f' v({i})'
                    break
        self.route = route
        return 0

    def get_absolute_url(self):
        return url_for('blog_bp.show_blog', blog_route=self.route)

    def get_date(self):
        return f'{self.post_date.strftime("%b")} {self.post_date.day}, {self.post_date.year}'

    def get_formatted_post_date(self):
        return format_date(self.post_date)

    def get_formatted_title(self, max_):
        # formatted = ' '.join(self.title.split()) if len(self.title) < 21 else ' '.join(self.title.split()[0:2])
        if len(self.title) >= max_ and len(self.title.split()) > 1:
            formatted = ''
            split_title = self.title.split()
            for word in split_title:
                if len(f"{formatted + ' ' + word}") < max_:
                    formatted += ' ' + word
                else:
                    break
            if formatted[-1] == ',':
                return formatted[0:-1] + '...'
            formatted += '' if formatted[-1] == '.' and formatted[-2] != '.' else '...'
            return formatted
        else:
            return self.title if len(self.title) < max_ else f'{self.title[0:max_ - int(max_ * 0.15)]}...'


    def content_preview(self):
        if len(self.content) <= 60 and len(self.content.split()) > 1:
            if len(self.content.split('.')) > 1:
                formatted = ''
                split_content = self.content.split('.')
                for string in split_content:
                    if len(f"{formatted + ' ' + string}") < 60:
                        formatted += ' ' + string
                    else:
                        slit_string = string.split()
                        for word in slit_string:
                            if len(f"{formatted + ' ' + string}") < 60:
                                formatted += ' ' + word
                            else:
                                break
                if formatted[-1] == ',':
                    return formatted[0:-1] + '...'
                formatted += '' if formatted[-1] == '.' and formatted[-2] != '.' else '...'
                return formatted
            else:
                return self.content if len(self.content) < 60 else f'{self.content[0:50]}...'
        else:
            return self.content if len(self.content) < 60 else f'{self.content[0:50]}...'


class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), default='Anonymous', nullable=True)
    content = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_posted = db.Column(db.Boolean, default=False)
    notified = db.Column(db.Boolean, default=False)

    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id', ondelete="CASCADE"))

    # blog = db.relationship('Blog', backref=backref('comments', passive_deletes=True))

    def __str__(self):
        return f'{self.content}'

    def get_date(self):
        return f'{self.post_date.strftime("%b")} {self.post_date.day}, {self.post_date.year}'

    def get_formatted_post_date(self):
        return format_date(self.post_date)
