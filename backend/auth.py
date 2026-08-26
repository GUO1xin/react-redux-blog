from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
from flask import current_app, g, jsonify, request

from models import User


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=current_app.config['JWT_EXP_DAYS']),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')


def _extract_user():
    header = request.headers.get('Authorization', '')
    if not header.startswith('Token '):
        return None

    token = header[len('Token '):].strip()
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None

    return User.query.get(payload.get('user_id'))


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = _extract_user()
        if user is None:
            return jsonify({'errors': {'auth': ['需要登录后才能操作']}}), 401
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper


def login_optional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        g.current_user = _extract_user()
        return fn(*args, **kwargs)
    return wrapper
