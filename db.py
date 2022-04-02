from flask_sqlalchemy import SQLAlchemy

### Instantiate SQLAlchemy ###
db = SQLAlchemy()

# SQLAlchemy instance initiation
def db_init(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()
