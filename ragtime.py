# from app import app
from app import create_app, db
import os
from app.models import Composition, Role, User, Follow
from flask_migrate import upgrade


# need to set ENV FLASK_CONFIG
app = create_app(os.environ.get("FLASK_CONFIG") or "default")

# [PROBABLY SOMETHING WITH MIGRATE/SHELL CONTEXT PROCESSOR]
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User, Composition=Composition, Follow=Follow)

@app.cli.command()
def deploy():
    """ Run deployment tasks such as upgrading database, inserting roles"""
    # migrate database
    upgrade()

    Role.insert_roles()

    User.add_self_follows()

# set FLASK_APP = ragtime.py

#TODO
# how to import create_app