from flask import render_template, Blueprint
from flask_bootstrap import Bootstrap

# if the line below is there because it would be stuck
# because it didn't exist yet main
#from . import views


main = Blueprint('main', __name__)

from . import views, errors

# routes are not registering
