from flask import render_template,  Blueprint

auth = Blueprint('auth' ,__name__)

from . import views, errors
