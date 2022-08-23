from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from config import configs
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
bootstrap = Bootstrap()
"""
Database Models...
LoginManager User Loader...
"""
def create_app(config_name='default'):
    app = Flask(__name__)
    # old way: app.config.from_pyfile('config.py')
    config_class = configs[config_name]

    # configuration settings are loaded through the from_object() method
    app.config.from_object(config_class)

    # he configuration class init_app() static method
    # is called to do any remaining setup for the app
    config_class.init_app(app)
    @app.route('/')

    #TODO remove this index function as it is extra
    def index():
         # Code for index route...
        """
        Your other routes and error handlers here...
        """
    return app

new_app = create_app()


