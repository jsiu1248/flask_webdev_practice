# config.py
# imports and such...

import os
basedir = os.path.abspath(os.path.dirname(__file__))

# https://stackoverflow.com/questions/58709973/vscode-1-39-x-python-3-7-x-importerror-attempted-relative-import-with-no-kn
# now the relative imports are seen properly by the debugger. without this, it was erroring out saying it didn't know which package it was from
PYTHONPATH = "./tests/:./"


# base config
class Config:
    SECRET_KEY = "keep it secret, keep it safe"
    SQLALCHEMY_DATABASE_URI =\
         'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
        # Flask-Mail config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Other email settings
    # email for the administrator of the flask app
    RAGTIME_ADMIN = os.environ.get('RAGTIME_ADMIN')

    # this will be the prefix everytime an emails is sent
    RAGTIME_MAIL_SUBJECT_PREFIX = 'Ragtime — '

    # when an email is sent to a user, it is set to this value
    RAGTIME_MAIL_SENDER = f'Ragtime Admin <{RAGTIME_ADMIN}>'

    # export MAIL_USERNAME=<your Gmail username>
    # remember to change it to your app password
    # export MAIL_PASSWORD=<your Gmail app password>
    # don't include spaces. It didn't like it

    @staticmethod
    def init_app(app):
        pass
configs = {'default': Config}

# getting breakpoints, traces, and reloaders
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_DEV_URL') or \
         'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

# for unit testing
class TestingConfig(Config):
    # making sure that these have names related to testing
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL') or \
'sqlite:///{os.path.join(basedir, "data-test.sqlite")}'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
f'sqlite:///{os.path.join(basedir, "data.sqlite")}'

# giving them all names
configs = {
     'development': DevelopmentConfig,
     'testing': TestingConfig,
     'production': ProductionConfig,
     'default': DevelopmentConfig
}