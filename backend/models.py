import re
import secrets
from datetime import datetime

from extensions import db

DEFAULT_AVATAR = 'https://api.realworld.io/images/smiley-cyrus.jpeg'

article_tags = db.Table(
    'article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
)

favorites = db.Table(
    'favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
)

follows = db.Table(
    'follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
)


def slugify(title):
    slug = re.sub(r'[^a-z0-9一-龥]+', '-', title.strip().lower()).strip('-')
    return slug or 'article'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, default='')
    image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    articles = db.relationship('Article', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    favorited_articles = db.relationship(
        'Article', secondary=favorites,
        backref=db.backref('favorited_by', lazy='dynamic'),
        lazy='dynamic',
    )

    followed = db.relationship(
        'User', secondary=follows,
        primaryjoin=(follows.c.follower_id == id),
        secondaryjoin=(follows.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic',
    )

    def is_following(self, user):
        return self.followed.filter(follows.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def has_favorited(self, article):
        return self.favorited_articles.filter(favorites.c.article_id == article.id).count() > 0

    def to_profile(self, current_user=None):
        return {
            'username': self.username,
            'bio': self.bio or '',
            'image': self.image or DEFAULT_AVATAR,
            'following': bool(current_user and current_user.id != self.id and current_user.is_following(self)),
        }

    def to_dict(self, token=None):
        return {
            'username': self.username,
            'email': self.email,
            'bio': self.bio or '',
            'image': self.image or DEFAULT_AVATAR,
            'token': token,
        }


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = db.relationship('Tag', secondary=article_tags, backref='articles', lazy='subquery')
    comments = db.relationship('Comment', backref='article', lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def generate_slug(title):
        base = slugify(title)
        slug = base
        while Article.query.filter_by(slug=slug).first():
            slug = f'{base}-{secrets.token_hex(3)}'
        return slug

    def to_dict(self, current_user=None):
        return {
            'slug': self.slug,
            'title': self.title,
            'description': self.description or '',
            'body': self.body or '',
            'tagList': sorted(tag.name for tag in self.tags),
            'createdAt': self.created_at.isoformat() + 'Z',
            'updatedAt': self.updated_at.isoformat() + 'Z',
            'favorited': bool(current_user and current_user.has_favorited(self)),
            'favoritesCount': self.favorited_by.count(),
            'author': self.author.to_profile(current_user),
        }


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, current_user=None):
        return {
            'id': self.id,
            'body': self.body,
            'createdAt': self.created_at.isoformat() + 'Z',
            'updatedAt': self.updated_at.isoformat() + 'Z',
            'author': self.author.to_profile(current_user),
        }
