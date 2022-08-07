# config.py
# imports and such...

import os
basedir = os.path.abspath(os.path.dirname(__file__))

# base config
class Config:
    SECRET_KEY = "keep it secret, keep it safe"
    SQLALCHEMY_DATABASE_URI =\
         'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
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
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL') or \
         'sqlite:///{os.path.join(basedir, "data-test.sqlite")}''

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