from app import create_app, current_app, db
from app.models import User

def test__app_creation():
    # creating an app instance with the testing configuration
    app = create_app('testing')
    # making sure that the app is defined
    assert app

def test_current_app():
    app = create_app('testing')
    # keeping track of the application-level data and pushing that
    app.app_context().push()

    # making sure current_app is defined
    assert current_app
    assert current_app.config['TESTING']
    # use python -m pytest to run tests in the future

def test_database_insert():
    app = create_app('testing')
    assert app.config['TESTING']
    # ensure test database configured
    assert 'data-test.sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
    app.app_context().push()
    # create all tables if not created
    db.create_all()

    u = User(email='john@example.com', username='john')
    db.session.add(u)
    db.session.commit()

    # IMPORTANT clear database for future tests
    # it is good to know that your tests begin with a clean or known state
    # app won't be changing but db would be changing 
    db.session.remove()
    db.drop_all()