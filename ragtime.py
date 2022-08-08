from app import app
from app import create_app
import os

# need to set ENV FLASK_CONFIG
app = create_app(os.environ.get("FLASK_CONFIG") or "default")

# [PROBABLY SOMETHING WITH MIGRATE/SHELL CONTEXT PROCESSOR]
# set FLASK_APP = ragtime.py

#TODO
# how to import create_app