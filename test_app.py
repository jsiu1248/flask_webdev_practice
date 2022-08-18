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