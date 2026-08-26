from flask import Blueprint, jsonify

from models import Tag

bp = Blueprint('tags', __name__)


@bp.route('/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify({'tags': [tag.name for tag in tags]})
