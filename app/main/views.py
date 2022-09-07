
# can't just import like normal because we are in a Blueprint
# have to do it in a way that it records the actions
from . import main # from this package import main object
from flask import render_template, session, redirect, url_for, flash
from .forms import NameForm # need a period because trying to import within package
from .. import db
from ..models import User, Role
from flask_login import login_required
from flask_bootstrap import Bootstrap

# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, User=User, Role=Role)

@main.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    # more code for index route...
    return render_template("index.html")

@main.route('/user/<username>')
def user(username):
    return render_template("user.html", user_name=username)



@main.route('/top-secret')
@login_required
def top_secret():
    return "Welcome, VIP member!"