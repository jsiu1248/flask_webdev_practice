from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
bootstrap = Bootstrap()
"""
Database Models...
LoginManager User Loader...
"""
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "keep it secret, keep it safe"
    app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    bootstrap.init_app(app) # extension initialization
    db.init_app(app) # another extension initialization
    @app.route('/')
    def index():
         # Code for index route...
        """
        Your other routes and error handlers here...
        """
    return app
