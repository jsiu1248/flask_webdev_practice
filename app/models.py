 
from . import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from flask_login import UserMixin


class Permission:
    FOLLOW = 1
    REVIEW = 2
    PUBLISH = 4
    MODERATE = 8
    ADMIN = 16

class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    # linking the role model and the user model
    users = db.relationship('User', backref='role', lazy = 'dynamic')
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)

    # overriding constructor of the Role class
    # so, we can set Permissions to 0, if the permissions were not initially set
    def __init__ (self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0


    # returning a string with the name
    def __repr__(self):
        return f"<Role {self.name}>"

    # helper function to help with permissions
    # checking if there is a permission and then adding it if there is NOT
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions = self.permissions + perm
    
    # checking if there is a permission then substracting if there IS 
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions = self.permissions - perm

    def reset_permission(self):
        self.permissions = 0

    # check if role has a particular permission
    # if the permission is greater than 0 then it has a particular permission
    def has_permission(self, perm):
        return self.permissions & perm == perm
    
class User(UserMixin, db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # age = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique = True, index = True)

    # errors out when someone tries to read it
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    #allow the user to still write a password
    @password.setter
    def password(self, password):
        # flask already has a function that helps with hashing and adding salt
        self.password_hash = generate_password_hash(password)

    # if you can't check your password, how do you know it is correct?
    # it takes the password and hash together and returns true if correct
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # login manager needs help with getting users
    # LoginManager will call load_user() to find out info about users
    # takes an id and returns the user
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"<User {self.username}>"
