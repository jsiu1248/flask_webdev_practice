
import pytest
from app import db, create_app

@pytest.fixture
def new_app(scope = 'module'):
    # create an instance of the app
    app = create_app('testing')

    # create app_context
    context = app.app_context()

    # pushes app context
    context.push()

    # create tables of database
    db.create_all()

    # yield an app instance
    yield app

    # tear down database
    db.clean_up()
    db.drop_all()

    # tear down app_context
    app.clean_up()

