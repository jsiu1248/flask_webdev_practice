from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

# can add new decorators that restrict access to routes bases on permissions

# decorator takes permission and checks
def permission_required(permission):
    """ Function decorator used so that only those
    who have been confirmed can access

    Args: permission (int): The permission given based on the list in Perission class from app.models 
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # check if use has that permission
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# piggy backs on the other decorator and checks if user has ADMIN permission
def admin_required(f):
    """ Function decorator that only admins can access
    """
    return permission_required(Permission.ADMIN)(f)
