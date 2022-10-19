from flask_httpauth import HTTPBasicAuth
from . import api
from ..models import User
from .errors import forbidden, unauthorized

# in order to auth a user via http, the user has to send their credentials through the Authorization request header.
# this is a wrapper
auth = HTTPBasicAuth()

# returns True if user verfication is successful
@auth.verify_password
def verify_password(email_or_token, password):
    # email_or_token is just an email for now
    if email_or_token == '':
        return False
    # if user is found then verify with password
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    # after auth then the auth user can be accessed later with g.
    g.current_user = user
    return user.verify_password(password)


@auth.error_handler
def auth_error():
# if auth not successful then send 401 error saying auth not successful
    return unauthorized('Invalid credentials')