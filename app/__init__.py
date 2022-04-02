"""
This contains the application factory for creating flask application instances.
Using the application factory allows for the creation of flask applications configured
for different environments based on the value of the CONFIG_TYPE environment variable
"""

import os
from flask import Flask, render_template, redirect, url_for, flash, Markup
from flask_admin import Admin
from flask_caching import Cache
from flask_mail import Mail
from flask_wtf import CSRFProtect
from celery import Celery

from .management import fill_db
from .utils.admin import BlogModelAdmin, BloggerModelAdmin, CommentModelAdmin, AdminHomeView
from .utils.security import initialize_security
from app.models import Blog, Blogger, Comment
from config import Config
from db import db

### Flask extension objects instantiation ###

admin = Admin()
csrf = CSRFProtect()
mail = Mail()
# login_manager = LoginManager()

### Instantiate Celery ###
celery = Celery(__name__,
                broker=Config.CELERY_BROKER_URL,
                result_backend=Config.RESULT_BACKEND,
                include=Config.include)

### Instantiate Cache ###
cache = Cache()

### Application Factory ###
def create_app():
    app = Flask(__name__)

    # Configure the flask app instance
    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object(CONFIG_TYPE)
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

    # Initialize SQLAlchemy object
    db_init(app)

    # Configure celery
    celery.conf.update(app.config)

    # Configure cache object
    cache.init_app(app, app.config)

    # Initialize security object
    initialize_security(app)

    # Register blueprints
    register_blueprints(app)

    # Initialize flask extension objects
    initialize_extensions(app)

    # Configure logging
    configure_logging(app)

    # Register error handlers
    register_error_handlers(app)

    # Register cli commands
    @app.cli.command("load_fixtures")
    def load_fixtures():
        fill_db()

    @app.route('/')
    def hello_world():  # put application's code here
        flash(Markup('Simple web application based on <a href="https://pypi.org/project/Flask/" class="red">Flask</a>, created by <a href="https://github.com/KhvPaul" class="red">@KhvPaul</a>'), 'success')
        return redirect(url_for('blog_bp.blog_list'), 302)

    return app


### Helper Functions ###

def db_init(app):
    from db import db_init
    db_init(app)


def register_blueprints(app):
    from app.auth import auth_blueprint
    from app.blog import blog_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(blog_blueprint, url_prefix='/blog')


def initialize_extensions(app):
    # flask_admin extension
    admin.init_app(app, index_view=AdminHomeView())

    admin.add_view(BloggerModelAdmin(Blogger, db.session))
    admin.add_view(BlogModelAdmin(Blog, db.session))
    admin.add_view(CommentModelAdmin(Comment, db.session))

    # flask_wtf CSRFProtect extension
    csrf.init_app(app)

    # flask_mail extension
    mail.init_app(app)

    # # flask_login extension
    # login_manager.init_app(app)
    #
    # login_manager.blueprint_login_view = {'auth': '/auth/login'}
    # login_manager.blueprint_login_views = {
    #     'auth': '/auth',
    #     'blog': '/blog',
    # }

    # @login_manager.user_loader
    # def load_user(pk):
    #     from db import db
    #     return db.session.query(Blogger).get(pk)


def register_error_handlers(app):
    # 400 - Bad Request
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error/400.html'), 400

    # 403 - Forbidden
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error/403.html'), 403

    # 404 - Page Not Found
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    # 405 - Method Not Allowed
    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('error/405.html'), 405

    # 405 - Method Not Allowed
    @app.errorhandler(413)
    def request_entity_too_large(e):
        flash('413: Request Entity Too Large', 'danger')
        return redirect(url_for('auth.authenticated_user_profile'), 302)

    # 500 - Internal Server Error
    @app.errorhandler(500)
    def server_error(e):
        return render_template('error/500.html'), 500


def configure_logging(app):
    pass
