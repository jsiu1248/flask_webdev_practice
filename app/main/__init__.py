from flask import render_template, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm


main = Blueprint('main', __name__, template_folder='templates',
url_prefix='main')