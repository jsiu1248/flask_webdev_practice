from flask import jsonify, request, g, url_for, current_app
from app import db
from ..models import Composition
from . import api
from .. models import Permission
from ..decorators import permission_required
from .errors import forbidden
from functools import wraps


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

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden("Insufficient permissions")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@api.route('/compositions/<int:id>', methods=['PUT'])
@permission_required(Permission.PUBLISH)
def edit_composition(id):
    composition = Composition.query.get_or_404(id)
    if g.current_user != composition.artist and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    import json
    put_json = json.loads(request.json)
    composition.release_type = put_json.get('release_type', composition.release_type)
    composition.title = put_json.get('release_type', composition.title)
    composition.description = put_json.get('description', composition.description)
    db.session.add(composition)
    db.session.commit()
    return jsonify(composition.to_json())

@api.route('/compositions/')
def get_compositions():
    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.paginate(
        page,
        per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
        error_out=False)
    compositions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_compositions', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_compositions', page=page+1)
    return jsonify({
        'compositions': [composition.to_json() for composition in compositions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })