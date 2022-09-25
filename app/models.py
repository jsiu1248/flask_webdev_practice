 
from email.policy import default
from . import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from flask_login import UserMixin

# They are all in CAPS because they are constants and shouldn't change. 
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

    # help automate main roles for app
    # mapping of role names with their permissions
    # as long as it doesn't find a role with the same name, it will add it and won't duplicate
    @staticmethod
    def insert_roles():
        roles = {
            'User':             [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH],
            'Moderator':        [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH,
                                 Permission.MODERATE],
            'Administrator':    [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH,
                                 Permission.MODERATE,
                                 Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            # see if role is already in table
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # it's not so make a new one
                role = Role(name=r)
            role.reset_permission()
            # add whichever permissions the role needs
            for perm in roles[r]:
                role.add_permission(perm)
            # if role is the default one, default is True
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


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
    confirmed = db.Column(db.Boolean, default = False)

    # we want to assign the users their roles right away
    # user constructor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # checking if it is ADMIN, and it is then giving it the admin role
        if self.role is None:
            if self.email == current_app.config['RAGTIM_ADMIN']:
                self.role = Role.query.filter_by(name = 'Administrator').first()
            # if not an admin then it gets a normal user role
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()


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

    # check if user can do something
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)


    # check if the user is an admin
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # in order to have the same helper methods for any user, you have to add the same for the anoynomous user or people who don't have account
    class AnonymousUser(AnonymousUserMixin):
        def can(self, perm):
            return False
        def is_administrator(self):
            return False
    
    # have to let login_manager know about the new class through the anonymous_user attribute
    login_manager.anonymous_user = AnonymousUser

    # login manager needs help with getting users
    # LoginManager will call load_user() to find out info about users
    # takes an id and returns the user
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"<User {self.username}>"
