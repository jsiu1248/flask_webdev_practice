from flask import render_template, Blueprint
from flask_bootstrap import Bootstrap



main = Blueprint('main', __name__, template_folder='templates',
url_prefix='/main')

from . import views, errors

# routes are not registering
