# This bluepint will deal with all user management functionality

from flask import Blueprint

blog_blueprint = Blueprint('blog_bp', __name__, template_folder='templates')

from . import views
