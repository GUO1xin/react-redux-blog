from flask import Blueprint, g, jsonify, request

from auth import login_optional, login_required
from extensions import db
from models import Article, Comment

bp = Blueprint('comments', __name__)


@bp.route('/articles/<slug>/comments', methods=['GET'])
@login_optional
def list_comments(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'errors': {'article': ['未找到']}}), 404

    comments = article.comments.order_by(Comment.created_at.desc()).all()
    return jsonify({'comments': [comment.to_dict(g.current_user) for comment in comments]})


@bp.route('/articles/<slug>/comments', methods=['POST'])
@login_required
def create_comment(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'errors': {'article': ['未找到']}}), 404

    data = (request.get_json(force=True) or {}).get('comment', {})
    body = (data.get('body') or '').strip()
    if not body:
        return jsonify({'errors': {'body': ['不能为空']}}), 422

    comment = Comment(body=body, article_id=article.id, author_id=g.current_user.id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'comment': comment.to_dict(g.current_user)})


@bp.route('/articles/<slug>/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(slug, comment_id):
    comment = Comment.query.get(comment_id)
    if not comment or comment.article.slug != slug:
        return jsonify({'errors': {'comment': ['未找到']}}), 404
    if comment.author_id != g.current_user.id:
        return jsonify({'errors': {'comment': ['无权删除']}}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({})
