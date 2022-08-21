
import pytest
from app import db, create_app

@pytest.fixture(scope = 'module') # the scope is module so all tests that use the fixture will use the test app instance
def new_app():
    """
    Tests that the database works when creating an app with the testing config.
    """
    # create an instance of the app
    app = create_app('testing')

    assert 'data-test.sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
    test_client = app.test_client() # why is test_client needed

    # he called it ctx. What does that stand for?
    # create app_context
    context = app.app_context()

    # pushes app context
    context.push()

    # create tables of database
    db.create_all()

    # yield an app instance
    yield test_client

    # tear down database
    # IMPORTANT clear database for future tests
    # it is good to know that your tests begin with a clean or known state
    # app won't be changing but db would be changing 
    db.session.remove()
    db.drop_all() # why is teardown this way?

    # tear down app_context
    app.pop() # how does it work?

