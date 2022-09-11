from flask import render_template, session, redirect, url_for, flash, current_app, request
from .forms import LoginForm # need a period because trying to import within package
from flask_login import login_user
from .. import db
from ..models import User, Role
from flask_login import login_required, logout_user, login_user
from flask_bootstrap import Bootstrap
from . import auth

@auth.route('/login' , methods=["GET", "POST"])
def login():
    # form is created
    form = LoginForm()

    # form is validated

        # query database for user
        # if user exists and the password is correct
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
    return render_template("auth/login.html", form = form
    )

@auth.route('/register', methods=["GET", "POST"])
def register():
    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out successfully")
    return redirect(url_for('main.index'))