from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from config import configs
from flask_migrate import Migrate
from flask_login import LoginManager
# from .models import User, Role


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()
login_manager = LoginManager()

# view function that acts like the login page
login_manager.login_view = 'auth.login'

"""
Database Models...
LoginManager User Loader...
"""
def create_app(config_name='default'):
    app = Flask(__name__)


    # old way: app.config.from_pyfile('config.py')
    config_class = configs[config_name]
    
    # initalize bootstrap and the db connection
    config_class.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    
    # configuration settings are loaded through the from_object() method
    app.config.from_object(config_class)
    
    from .main import main  # curly braces mean package in vscode
    app.register_blueprint(main)

    # he configuration class init_app() static method
    # is called to do any remaining setup for the app
 

    """


    #TODO remove this index function as it is extra
    @app.route('/')
    def index_app():
         # Code for index route...
        
        return 'hello this is the index'
    """
    return app

new_app = create_app()

