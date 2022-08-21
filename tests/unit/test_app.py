from app import create_app, current_app, db
from app.models import User


def test_database_insert(new_app):
    u = User(email='john@example.com', username='john')
    db.session.add(u)
    db.session.commit()

