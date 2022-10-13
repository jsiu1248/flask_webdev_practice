
# can't just import like normal because we are in a Blueprint
# have to do it in a way that it records the actions
# may have some kind of cache and finds main as a key and then value of that is a blueprint
from . import main # from this package import main object
from flask import render_template, session, redirect, url_for, flash, current_app, request, abort
from .forms import NameForm, EditProfileForm, AdminLevelEditProfileForm, CompositionForm # need a period because trying to import within package
from .. import db
from ..models import User, Role, Permission, Composition
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

@main.route('/', methods=['GET', 'POST'])
def index():
    form = CompositionForm()
    if current_user.can(Permission.PUBLISH) \
            and form.validate_on_submit():
        composition = Composition(
            release_type=form.release_type.data,
            title=form.title.data,
            description=form.description.data,

            # current user is link current_app being a proxy for the current_user and no the actual User
            # current_user is a shortcut. it already knows what object you want
            artist=current_user._get_current_object()
            )
        db.session.add(composition)
        db.session.commit()
        # must be generated after first commit because it depends on composition's id
        composition.generate_slug()
        return redirect(url_for('.index'))
    
    # determining the page to render and the default page is 1
    page = request.args.get('page', 1, type=int)
    # all is replaced by paginate
    pagination = \
        Composition.query.order_by(Composition.timestamp.desc()).paginate(
            page,
            per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
            error_out=False)
    # the items are the results of the particular page        
    compositions = pagination.items
    return render_template(
        'index.html',
        form=form,
        compositions=compositions,
        pagination=pagination
    )

# route will pass user_name variable
@main.route('/user/<username>')
def user(username):
    # query user or return error
    user = User.query.filter_by(username = username).first_or_404()
    page = request.args.get('page', 1, type = int)
    # Pagination of the compositions for user
    pagination = Composition.query.filter_by(artist=user).order_by(Composition.timestamp.desc()).paginate(
            page,
            per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
            error_out=False)
    # Convert to list
    compositions = pagination.items
    return render_template('user.html', user=user, compositions=compositions, pagination=pagination)


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
    """
    Admin access to editting other's profiles. Admin access and login is required. 
    Args: id of user
    """
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


@main.route('/composition/<slug>')
@login_required
def composition(slug):
    # passes composition contained in a list respresented as compositions to template
    composition = Composition.query.filter_by(slug=slug).first_or_404()
    return render_template('composition.html', compositions=[composition])

@main.route('/edit/<slug>')
@login_required
def edit_composition(slug):
    """
    Edit each composition. Login is required. 
    Args: slug
    """
    form = CompositionForm()
    # searches for composition by slug or 404
    composition = Composition.query.filter_by(slug=slug).first_or_404()
    # if not the user nor admin abort
    if current_user.username != composition.artist and not current_user.can(Permission.ADMIN):
        abort(403)  
    if form.validate_on_submit():
        composition.release_type = form.release_type.data
        composition.title = form.title.data
        composition.description = form.description.data
        composition.generate_slug()
        db.session.add(composition)
        db.session.commit()
        flash("Composition updated")

        # which slug is it directing to?
        return redirect(url_for('.composition', slug = composition.slug))
        
    # why is the data equaled back and forth - seems like it is doing the same thing twice
    form.release_type.data = composition.release_type
    form.title.data = composition.title
    form.description.data = composition.description
    return render_template('edit_composition.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    """ follow a destinated user and making sure the user exists and if they are already following them.
    Args: user who you want to follow
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash("Looks like you are already following that user.")
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You are now following {username}")
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    """ unfollow a user. Checks if following already
    Args: user who you want to unfollow
    Returns: user.html takes you back to user profile"""
    user = User.query.filter_by(username=username).first()
    # if not a user
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    # if not already following that user
    if not current_user.is_a_follower(user):
        flash("You are not following that user.")
        return redirect(url_for('.user', username=username))
    # unfollow user and take row out from database
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You have unfollowed {username}")
    # redirects to user profile
    return redirect(url_for('.user', username=username))






@main.route('/followers/<username>')
def followers(username):
    """ Get and paginate users. Get the user in question and if they don't exist then go 
    through a notification. A pagination object is created from the user's followers. Query for followers returns a list of
    follow instances. Only the follower users are needed. Another list is created that gives only
    the follower users and the timestamp
        Args: username (str): name of the user who has followers
        Returns: followers.html returns a page displaying the followers of the user
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config['RAGTIME_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # convert to only follower and timestamp
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',
                           user=user,
                           title_text="Followers of",
                           endpoint='.followers',
                           pagination=pagination,
                           follows=follows)





@main.route('/following/<username>')
def following(username):
    """
    Show users a particular user is already following
    Args: username(str) : showing who this user follows
    Return: following.html returns page displaying user following who
    """
    user = User.query.filter_by(username=username).first()
    # if not a user
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    # display page with list of users who user is following
    pagination = user.following.paginate(
        page,
        per_page=current_app.config['RAGTIME_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # convert to only follower and timestamp
    follows = [{'user': item.following, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('following.html',
                           user=user,
                           title_text="Following",
                           endpoint='.following',
                           pagination=pagination,
                           follows=follows)
