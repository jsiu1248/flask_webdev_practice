from flask import render_template, session, redirect, url_for, flash
# from .forms import NameForm # need a period because trying to import within package
from .. import db
from ..models import User, Role
from flask_login import login_required, logout_user, login_user
from flask_bootstrap import Bootstrap

from . import auth

@auth.route('/login' , methods=["GET", "POST"])
def login():
    return render_template("auth/login.html")

@auth.route('/register', methods=["GET", "POST"])
def register():
    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out successfully")
    return redirect(url_for('main.index'))