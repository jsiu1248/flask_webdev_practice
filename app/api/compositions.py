from flask import jsonify
from ..models import Composition
from . import api

@api.route('/compositions/')
def get_compositions():
    """
    takes compositions. Then jsonify the objects one by one.
    """
    compositions = Composition.query.all()
    return jsonify({ 'compositions': [composition.to_json()
                                      for composition in compositions]})