from flask import Blueprint, g, jsonify, request

from auth import check_password, generate_token, hash_password, login_required
from extensions import db
from models import User

bp = Blueprint('users', __name__)


@bp.route('/users', methods=['POST'])
def register():
    data = (request.get_json(force=True) or {}).get('user', {})
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    errors = {}
    if not username:
        errors.setdefault('username', []).append('不能为空')
    elif User.query.filter_by(username=username).first():
        errors.setdefault('username', []).append('已被占用')
    if not email:
        errors.setdefault('email', []).append('不能为空')
    elif User.query.filter_by(email=email).first():
        errors.setdefault('email', []).append('已被注册')
    if len(password) < 6:
        errors.setdefault('password', []).append('至少需要6位')

    if errors:
        return jsonify({'errors': errors}), 422

    user = User(username=username, email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({'user': user.to_dict(token=generate_token(user))})


@bp.route('/users/login', methods=['POST'])
def login():
    data = (request.get_json(force=True) or {}).get('user', {})
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password_hash):
        return jsonify({'errors': {'email or password': ['不正确']}}), 401

    return jsonify({'user': user.to_dict(token=generate_token(user))})


@bp.route('/user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({'user': g.current_user.to_dict()})


@bp.route('/user', methods=['PUT'])
@login_required
def update_current_user():
    data = (request.get_json(force=True) or {}).get('user', {})
    user = g.current_user

    if data.get('username'):
        user.username = data['username']
    if data.get('email'):
        user.email = data['email']
    if 'bio' in data:
        user.bio = data['bio']
    if 'image' in data:
        user.image = data['image']
    if data.get('password'):
        user.password_hash = hash_password(data['password'])

    db.session.commit()
    return jsonify({'user': user.to_dict()})
