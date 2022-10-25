from . import api
from flask import jsonify, request, current_app, url_for
from ..models import User, Composition

@api.route('/users/<int:id>')
# endpoint where app can receive client requests
def get_user(id):
    """
    takes user id and gets user. Then jsonify the object.
    """
    user = User.query.get_or_404(id)
    return jsonify(user.to_json()) 


@api.route('/users/<int:id>/compositions/', methods=["GET"])
def get_user_compositions(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    query = user.compositions
    pagination = query.order_by(Composition.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
        error_out=False)
    compositions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_compositions', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_compositions', id=id, page=page+1)
    return jsonify({
        'compositions': [composition.to_json() for composition in compositions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api.route('/users/<int:id>/followed/', methods=["GET"])
def get_user_followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    query = user.followed_compositions
    pagination = query.order_by(Composition.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
        error_out=False)
    compositions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_compositions', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_compositions', id=id, page=page+1)
    return jsonify({
        'compositions': [composition.to_json() for composition in compositions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })