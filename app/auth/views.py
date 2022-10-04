from flask import render_template, session, redirect, url_for, flash, current_app, request
from .forms import LoginForm, RegistrationForm # need a period because trying to import within package
from .. import db
from ..models import User, Role
from flask_login import login_required, logout_user, login_user, current_user
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from . import auth

@auth.route('/login' , methods=["GET", "POST"])
def login():
    # form is created
    form = LoginForm()

    # form is validated
    if form.validate_on_submit():
        # query database for user
        email_entered = form.email.data
        password_entered = form.password.data
        # query checking if the name is in the database
        user = User.query.filter_by(email = email_entered).first()
        print(user)
        # if user exists and the password is correct
        if user and user.verify_password(password_entered):
            login_user(user, form.remember_me.data)

            # query string is part of a url
            # pass arguments to a url 
            # variable tell flask where to go after the user logs in
            # google.com/?auth=ramble&key=value 
            next = request.args.get('next')

            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
            # flash a message that username/password is invalid
        flash("The username/password is invalid")
    return render_template("auth/login.html", form = form)

@auth.route('/register', methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email_entered = form.email.data
        password_entered = form.password.data
        username_entered = form.username.data
        # query checking if the name is in the database
        user = User.query.filter_by(email = email_entered).first()

        # it auto checks if the email is used already and same for the username


        u = User()
        u.email = email_entered
        u.username = username_entered
        u.password = password_entered

        db.session.add(u)
        db.session.commit()
        flash("You can now login.")
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form = form)

@auth.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out successfully")
    return redirect(url_for('main.index'))

# take a token and attempt to confirm the user and then redirect it back to the index page
# we want this to confirm the current_user because we don't want an old user
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash("You're already confirmed, silly!")
        return redirect(url_for('main.index'))
    
    # if the token is confirmed then the user is commited 
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account! Thank you.')
    else:
        flash("Whoops! That confirmation link either expired, or it isn't valid.")
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    # back slash means line continuation
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request != 'static' \
        and request.blueprint != 'auth' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)