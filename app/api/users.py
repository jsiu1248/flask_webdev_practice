from . import api
from flask import jsonify
from ..models import User

@api.route('/users/<int:id>')
# endpoint where app can receive client requests
def get_user(id):
    """
    takes user id and gets user. Then jsonify the object.
    """
    user = User.query.get_or_404(id)
    return jsonify(user.to_json()) 