from flask import Blueprint, render_template

main = Blueprint('main', __name__, template_folder='templates',
url_prefix='main')