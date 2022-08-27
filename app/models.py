 
from . import db 
from werkzeug.security import check_password_hash, generate_password_hash

class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    # linking the role model and the user model
    users = db.relationship('User', backref='role', lazy = 'dynamic')
    # returning a string with the name
    def __repr__(self):
        return f"<Role {self.name}>"

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    age = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))

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


    def __repr__(self):
        return f"<User {self.username}>"
