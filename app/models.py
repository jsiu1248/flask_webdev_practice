 
from email.policy import default
from . import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime, timedelta
import jwt
import hashlib
import bleach
import re
from itsdangerous import Serializer
from app.exceptions import ValidationError

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

class Follow(db.Model):
    __tablename__ = 'follows'

    # ID of the user who follows another
    follower_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
    # with both columns as primary key then both foreign keys form the primary key
                            primary_key=True)
    
    # ID of the user who is being followed
    following_id = db.Column(db.Integer,
                             db.ForeignKey('users.id'),
                             primary_key=True)
    # time the user started following
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # age = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique = True, index = True)
    confirmed = db.Column(db.Boolean, default = False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    # it will be assigned upon the created of the new User
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    compositions = db.relationship('Composition', backref='artist', lazy='dynamic')
    following = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.following_id],
                                backref=db.backref('following', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # we want to assign the users their roles right away
    # user constructor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # assert self.email is not None
        
        # the first time a user logs in, we will set their role
        # the next time, they log in they will skip this 
        if self.role is None:
            # checking if it is ADMIN, and it is then giving it the admin role
            print(self.email)
            if self.email == "flaskwebdev.js@gmail.com": #current_app.config['RAGTIME_ADMIN']:
                self.role = Role.query.filter_by(name = 'Administrator').first()
            # if not an admin then it gets a normal user role
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()
            
            # if email is not black then call the hash function
            if self.email is not None and self.avatar_hash is None:
                self.avatar_hash = self.email_hash()
        # all users are their own followers now
        self.follow(self)
    
    # creating a hash for the email
    def email_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def ping(self):
        """
        When a new request is made, last_seen is updated.
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

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

    # generates a token 
    # exp controls the time of expiration
    def generate_confirmation_token(self, expiration_sec=3600):
        # For jwt.encode(), expiration is provided as a time in UTC
        # It is set through the "exp" key in the data to be tokenized
        expiration_time = datetime.utcnow() + timedelta(seconds=expiration_sec)
        data = {"exp": expiration_time, "confirm_id": self.id}
        # Use SHA-512 (known as HS512) for the hash algorithm
        token = jwt.encode(data, current_app.secret_key, algorithm="HS512")
        return token

    # checks whether token is valid or not for user and have to make sure that they are logged in
    def confirm(self, token):
        try:
            # Ensure token valid and hasn't expired
            data = jwt.decode(token, current_app.secret_key, algorithms=["HS512"])
        except jwt.ExpiredSignatureError as e:
            # token expired
            return False
        except jwt.InvalidSignatureError as e:
            # key does not match
            return False
        # The token's data must match the user's ID
        if data.get("confirm_id") != self.id:
            return False
        # All checks pass, confirm the user
        self.confirmed = True
        db.session.add(self)
        # the data isn't committed yet as you want to make sure the user is currently logged in.
        return True

    def unicornify(self, size=128):
        """
        Each user is given it's own unique unicorn avatar. Uses the cached hash if avaliable and if not it creates one.

        Returns: Path directly to the image
        """
        url = 'https://unicornify.pictures/avatar'
        hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'{url}/{hash}?s={size}'

    def follow(self, user):
        """
        follows user. A new row is inserted in the follows table linking it to the user passed in
        Args: user that you want to follow
        """
        if not self.is_following(user):
            f = Follow(follower=self, following=user)
            db.session.add(f)

    def unfollow(self, user):
        """unfollows user. A row is deleted in the follows table linking the user  passed in 
        Args: user that you want to unfollow
        """
        f = self.following.filter_by(following_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        """ determines if you are following user
        Args: user that you want to see if you are following
        """
        if user.id is None:
            return False
        return self.following.filter_by(
            following_id=user.id).first() is not None

    def is_a_follower(self, user):
        """ determines if another user is a follower
        Args: user is or is not a follower
        """
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_compositions(self):
        """Joining Composition and Follow tables and the primary key on following_id and arist_id. And, we are filtering the ones that match so it feels
        as an inner join"""
        return Composition.query.join(
            Follow, Follow.following_id == Composition.artist_id)\
            .filter(Follow.follower_id == self.id)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def generate_auth_token(self, expiration_sec):
        s = Serializer(current_app.config['SECRET_KEY'],
                          expires_in=expiration_sec)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        # if a user token is successfully verified, the User corresponding to the token is returned.
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        # dictionary gives client info about user without sensitive
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'last_seen': self.last_seen,
            'compositions_url': url_for('api.get_user_compositions', id=self.id),
            'followed_compositions_url': url_for('api.get_user_followed', id=self.id),
            'composition_count': self.compositions.count()
        }
        return json_user

# in order to have the same helper methods for any user, you have to add the same for the anoynomous user or people who don't have account
# define the same methods as User to prevent any NameErrors where local or global name is not found
class AnonymousUser(AnonymousUserMixin):
    # checking that a user has a given permission and can perform a task
    def can(self, perm):
        return False
    def is_administrator(self):
        return False

class ReleaseType:
    SINGLE = 1
    EXTENDED_PLAY = 2
    ALBUM = 3


class Composition(db.Model):
    __tablename__ = 'compositions'
    id = db.Column(db.Integer, primary_key=True)
    release_type = db.Column(db.Integer)
    title = db.Column(db.String(64))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description_html = db.Column(db.Text)
    slug = db.Column(db.String(128), unique=True)

    @staticmethod
    def on_changed_description(target, value, oldvalue, initiator):
        """
        "listener" of SQLAlchemy's "set" event for description. the function will be called whenever the
        description changes.
        """
        allowed_tags = ['a']
        # clean is called, takes a list of allowed tags
        # linkify will make hyperlinks out of urls in text. <a> tags are created automatically 
        html = bleach.linkify(bleach.clean(value,
        # allowed tags is a whitelist
                                           tags=allowed_tags,
        # strip away any extra characters
                                           strip=True))
        target.description_html = html

    def generate_slug(self):
        """
        The slug is long enough for any title. REGEX is used to make it more readable and lowered.
        The id is added to make sure that it is unique. 
        """
        self.slug = f"{self.id}-" + re.sub(r'[^\w]+', '-', self.title.lower())
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        # dictionary gives client info about composition without sensitive
        json_user = {
            'url': url_for('api.get_composition', id=self.id),
            'release_type': self.release_type,
            'title': self.title,
            'description': self.description,
            'description_html': self.description_html,
            'timestamp': self.timestamp, 
            'artist_url': url_for('api.get_user', id=self.id)
        }
        return json_user

    @staticmethod
    def from_json(json_composition):
        """checking the json data is valid
        Args: JSON dictionary
        Returns: Composition
        """
        release_type = json_composition.get('release_type')
        title = json_composition.get('title')
        description = json_composition.get('description')
        # if the data is invalid then a validation error is used
        if release_type is None:
            raise ValidationError("Composition must have a release type")
        if title is None:
            raise ValidationError("Composition must have a title")
        if description is None:
            raise ValidationError("Composition must have a description")
        return Composition(release_type=release_type,
                           title=title,
                           description=description)



db.event.listen(Composition.description,
                'set',
                Composition.on_changed_description)
    
    # have to let login_manager know about the new class through the anonymous_user attribute
    # why does this need to be done again? Since in the definition is already named AnonymousUser
login_manager.anonymous_user = AnonymousUser

# login manager needs help with getting users
# LoginManager will call load_user() to find out info about users
# takes an id and returns the user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def __repr__(self):
    return f"<User {self.username}>"
