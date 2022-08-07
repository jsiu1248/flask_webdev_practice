import os
basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = "keep it secret, keep it safe"
SQLALCHEMY_DATABASE_URI =\
     'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False