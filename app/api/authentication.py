from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from . import api
from ..models import User
from .errors import forbidden, unauthorized, bad_request
from ..exceptions import ValidationError

# in order to auth a user via http, the user has to send their credentials through the Authorization request header.
# this is a wrapper
auth = HTTPBasicAuth()

# returns True if user verfication is successful
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        # called to grab the User assocaited with the token, which is stored in g.current_user
        # token_used is True when it is verified
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@auth.error_handler
def auth_error():
# if auth not successful then send 401 error saying auth not successful
    return unauthorized('Invalid credentials')

@api.route('/tokens/', methods=['POST'])
# get token double checks if the user is auth
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    # only auth users can get tokens
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration_sec=3600), 'expiration': 3600})

# making life easier because all requires who make api requests need to be logged in it
@api.before_request
# same name decorator from flask-httpauth
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')



@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])