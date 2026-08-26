from flask import Blueprint, g, jsonify, request

from auth import login_optional, login_required
from extensions import db
from models import Article, Tag, User

bp = Blueprint('articles', __name__)


def _get_or_create_tags(names):
    tags = []
    for name in names or []:
        name = name.strip()
        if not name:
            continue
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        tags.append(tag)
    return tags


def _paginate(query):
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    total = query.count()
    articles = (
        query.order_by(Article.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return articles, total


@bp.route('/articles', methods=['GET'])
@login_optional
def list_articles():
    query = Article.query

    tag = request.args.get('tag')
    if tag:
        query = query.join(Article.tags).filter(Tag.name == tag)

    author = request.args.get('author')
    if author:
        query = query.join(User, Article.author_id == User.id).filter(User.username == author)

    favorited = request.args.get('favorited')
    if favorited:
        favoriter = User.query.filter_by(username=favorited).first()
        if favoriter is None:
            return jsonify({'articles': [], 'articlesCount': 0})
        article_ids = [a.id for a in favoriter.favorited_articles]
        query = query.filter(Article.id.in_(article_ids or [-1]))

    articles, total = _paginate(query)
    return jsonify({
        'articles': [article.to_dict(g.current_user) for article in articles],
        'articlesCount': total,
    })


@bp.route('/articles/feed', methods=['GET'])
@login_required
def feed():
    followed_ids = [u.id for u in g.current_user.followed]
    query = Article.query.filter(Article.author_id.in_(followed_ids or [-1]))

    articles, total = _paginate(query)
    return jsonify({
        'articles': [article.to_dict(g.current_user) for article in articles],
        'articlesCount': total,
    })


@bp.route('/articles/<slug>', methods=['GET'])
@login_optional
def get_article(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'errors': {'article': ['未找到']}}), 404
    return jsonify({'article': article.to_dict(g.current_user)})


@bp.route('/articles', methods=['POST'])
@login_required
def create_article():
    data = (request.get_json(force=True) or {}).get('article', {})
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'errors': {'title': ['不能为空']}}), 422

    article = Article(
        title=title,
        description=data.get('description', ''),
        body=data.get('body', ''),
        author_id=g.current_user.id,
        slug=Article.generate_slug(title),
    )
    article.tags = _get_or_create_tags(data.get('tagList'))
    db.session.add(article)
    db.session.commit()

    return jsonify({'article': article.to_dict(g.current_user)})


@bp.route('/articles/<slug>', methods=['PUT'])
@login_required
def update_article(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'errors': {'article': ['未找到']}}), 404
    if article.author_id != g.current_user.id:
        return jsonify({'errors': {'article': ['无权修改']}}), 403

    data = (request.get_json(force=True) or {}).get('article', {})
    if data.get('title') and data['title'] != article.title:
        article.title = data['title']
        article.slug = Article.generate_slug(data['title'])
    if 'description' in data:
        article.description = data['description']
    if 'body' in data:
        article.body = data['body']
    if 'tagList' in data:
        article.tags = _get_or_create_tags(data['tagList'])

    db.session.commit()
    return jsonify({'article': article.to_dict(g.current_user)})


@bp.route('/articles/<slug>', methods=['DELETE'])
@login_required
def delete_article(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'errors': {'article': ['未找到']}}), 404
    if article.author_id != g.current_user.id:
        return jsonify({'errors': {'article': ['无权删除']}}), 403

    db.session.delete(article)
    db.session.commit()
    return jsonify({})


@bp.route('/articles/<slug>/favorite', methods=['POST'])
@login_required
def favorite(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'errors': {'article': ['未找到']}}), 404

    if not g.current_user.has_favorited(article):
        g.current_user.favorited_articles.append(article)
        db.session.commit()
    return jsonify({'article': article.to_dict(g.current_user)})


@bp.route('/articles/<slug>/favorite', methods=['DELETE'])
@login_required
def unfavorite(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'errors': {'article': ['未找到']}}), 404

    if g.current_user.has_favorited(article):
        g.current_user.favorited_articles.remove(article)
        db.session.commit()
    return jsonify({'article': article.to_dict(g.current_user)})
