from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from config import configs
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
# from .models import User, Role


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()
mail = Mail()
moment = Moment()

# instance of LoginManager
login_manager = LoginManager()

# view function that acts like the login page
# login_view attribute is set
# property specifies endpoint that LoginManger will direct a user if the user tried to access a protected page
# cam direct anonymous user to login page
# if there is login_required decorator
# since there are blueprints then have to direct it to the right place with a dot
# without setting attribute then it will fail sometime
# not making assumptions of login page
login_manager.login_view = 'auth.login'



def create_app(config_name='default'):
    app = Flask(__name__)


    # old way: app.config.from_pyfile('config.py')
    config_class = configs[config_name]
    
    # initalize bootstrap and the db connection
    # not all init_app does the same thing
    # think of more my app using the extension
    # initalize app with all of the things that sqlachelmy requires it to work
    # loading config before extensions use it
    app.config.from_object(config_class)

    config_class.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # set it up for flask all of the JS and quickform and templates
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # configuration settings are loaded through the from_object() method
    # taking classes members into a dictionary
    
    from .main import main as main_blueprint  # curly braces mean package in vscode
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint # curly braces mean package in vscode
    app.register_blueprint(auth_blueprint)

    from .api import api as api_blueprint # curly braces mean package in vscode
    app.register_blueprint(api_blueprint)

    # he configuration class init_app() static method
    # is called to do any remaining setup for the app
 

    return app
