from app import db # create_app, current_app
from app.models import User
import pytest

def test_database_insert(new_app):
    u = User(username='jon')
    db.session.add(u)
    db.session.commit()

def test_password_create(new_app):
    u = User(username="jon")
    u.password = 'corn'

def test_password_hash(new_app):
    u = User(username="jon", password = 'corn')
    # couldn't put u.password here because it doesn't take that attribute
    assert u.verify_password("corn")

def test_password_verify(new_app):
    u = User(username="jon", password = 'corn')
    assert not u.verify_password("not the password")
    
def test_password_access(new_app):
    u = User(username="jon", password = 'corn')
    with pytest.raises(AttributeError):
        print(u.password)

def test_different_users_same_password(new_app):
    u = User(username="jon", password = 'corn')
    u2 = User(username = "lorren", password='corn')
    assert u.password_hash is not u2.password_hash

