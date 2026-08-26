from flask import Blueprint, g, jsonify

from auth import login_optional, login_required
from extensions import db
from models import User

bp = Blueprint('profiles', __name__)


@bp.route('/profiles/<username>', methods=['GET'])
@login_optional
def get_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'errors': {'username': ['未找到该用户']}}), 404
    return jsonify({'profile': user.to_profile(g.current_user)})


@bp.route('/profiles/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'errors': {'username': ['未找到该用户']}}), 404

    g.current_user.follow(user)
    db.session.commit()
    return jsonify({'profile': user.to_profile(g.current_user)})


@bp.route('/profiles/<username>/follow', methods=['DELETE'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'errors': {'username': ['未找到该用户']}}), 404

    g.current_user.unfollow(user)
    db.session.commit()
    return jsonify({'profile': user.to_profile(g.current_user)})
