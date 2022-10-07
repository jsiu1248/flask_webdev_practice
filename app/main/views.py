
# can't just import like normal because we are in a Blueprint
# have to do it in a way that it records the actions
# may have some kind of cache and finds main as a key and then value of that is a blueprint
from . import main # from this package import main object
from flask import render_template, session, redirect, url_for, flash
from .forms import NameForm, EditProfileForm, AdminLevelEditProfileForm # need a period because trying to import within package
from .. import db
from ..models import User, Role, Permission
from flask_login import login_required, current_user
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

# route will require login and user to be an administrator
@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return f"Welcome, Administrator! {Permission.ADMIN}"

# route will require login and the user to have moderate permissions
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

    # session is imported by flask and the get function for key value access     
    return render_template('index.html', form=form, name=session.get('name'), known = session.get('known', False))

# route will pass user_name variable
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)


# route will require login
@main.route('/top-secret')
@login_required
def top_secret():
    return "Welcome, VIP member!"

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('You successfully updated your profile! Looks great.')
        return redirect(url_for('.user', username=current_user.username))

    # why is the data equaled back and forth - seems like it is doing the same thing twice
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('edit_profile.html', form=form)

@main.route('/editprofile/<int:id>', methods = ['GET', 'POST'])
@login_required
@admin_required
def admin_edit_profile(id):
    form = AdminLevelEditProfileForm()

    # Search for user based on ID and return 404 if None
    user = User.query.filter_by(id = id).first_or_404()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.confirmed = form.confirmed.data

        # filtering for the first role name by form.role.data
        current_user.role = Role.query.filter_by(id = form.role.data).first()
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('You successfully updated {user.username}\'s profile.')
        return redirect(url_for('.user', username=current_user.username))

    # why is the data equaled back and forth - seems like it is doing the same thing twice
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    form.username.data = current_user.username
    form.confirmed.data = current_user.confirmed
    form.role.data = current_user.role_id

    return render_template('edit_profile.html', form=form)
