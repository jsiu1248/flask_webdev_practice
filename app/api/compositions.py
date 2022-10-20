from flask import jsonify, request, g, url_for
from app import db
from ..models import Composition
from . import api
from .. models import Permission
from ..decorators import permission_required

@api.route('/compositions/')
def get_compositions():
    """
    takes compositions. Then jsonify the objects one by one.
    """
    compositions = Composition.query.all()
    return jsonify({ 'compositions': [composition.to_json()
                                      for composition in compositions]})

@api.route('/compositions/', methods=['POST'])
@permission_required(Permission.PUBLISH)
def new_composition():
    # deserializes composition
    # POST request to make a composition through API
    composition = Composition.from_json(request.json)
    composition.artist = g.current_user
    # adds composition to database
    db.session.add(composition)
    db.session.commit()
    # returns deserialized and again serialized composition and 201 and location header
    return jsonify(composition.to_json()), 201, \
        {'Location': url_for('api.get_composition', id=composition.id)}