
# can't just import like normal because we are in a Blueprint
# have to do it in a way that it records the actions
from . import main # from this package import main object
from flask import render_template
from .forms import NameForm # need a period because trying to import within package

@main.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    # more code for index route...
    return render_template("index.html")

@main.route('/user/<username>')
def user(username):
    return render_template("user.html", user_name=username)