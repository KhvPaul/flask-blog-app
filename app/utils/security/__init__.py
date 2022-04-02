# security
from flask_security import Security, SQLAlchemyUserDatastore

from app.models import Blogger, Role
from db import db
from .forms import SignUpForm

### Instantiate Security ###
# from .utils import MyMailUtil

security = Security()
user_datastore = SQLAlchemyUserDatastore(db, Blogger, Role)

# Security instance initiation
def initialize_security(app):
    security.init_app(app, user_datastore, register_form=SignUpForm)

