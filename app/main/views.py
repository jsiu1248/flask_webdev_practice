
# can't just import like normal because we are in a Blueprint
# have to do it in a way that it records the actions
# may have some kind of cache and finds main as a key and then value of that is a blueprint
from . import main # from this package import main object
from flask import render_template, session, redirect, url_for, flash
from .forms import NameForm # need a period because trying to import within package
from .. import db
from ..models import User, Role, Permission
from flask_login import login_required
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from ..decorators import permission_required, admin_required

# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, User=User, Role=Role)

# route comes first
# check if user is authenticated
# check permission
# topmost decorators are evaluated before the others

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "Welcome, Administrator!"

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "Greetings, moderator!"

@main.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()

    if form.validate_on_submit():
        # name=None # we need a session variable now instead
        name_entered = form.name.data
        # query checking if the name is in the database
        user = User.query.filter_by(username = name_entered).first()
        if user is None:
            # setting username to data that has just been entered
            user = User(username = name_entered)
            db.session.add(user)
            db.session.commit()
            # indicating that a user is new
            session['known'] = False
        else:
            # user does exist in the database?
            session['known'] = True
        session['name']= name_entered

        # name=form.name.data # we can clear the line because it already gets cleared
        form.name.data="" # what does this do?
        name_entered = form.name.data
        #whenever a post function happens then you can go back to get function so it doesn't error
        flash('Please enjoy this place!')
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known = session.get('known', False))


@main.route('/user/<username>')
def user(username):
    return render_template("user.html", user_name=username)



@main.route('/top-secret')
@login_required
def top_secret():
    return "Welcome, VIP member!"