from flask import render_template, Blueprint
from flask_bootstrap import Bootstrap
from ..models import Permission

# if the line below is there because it would be stuck
# because it didn't exist yet main
#from . import views


main = Blueprint('main', __name__)

from . import views, errors

# routes are not registering

# current_app and current_user were injected automatically by Flask and Flask-Login.
# So, you can do the same with app_context_processor
# You can inject Permissions into templates globally
@main.app_context_processor
def inject_permissions():
    return dict(Permission = Permission)