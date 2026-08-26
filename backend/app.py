from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, resources={r'/api/*': {'origins': app.config['CORS_ORIGIN']}})

    from routes.articles import bp as articles_bp
    from routes.comments import bp as comments_bp
    from routes.profiles import bp as profiles_bp
    from routes.tags import bp as tags_bp
    from routes.users import bp as users_bp

    for blueprint in (users_bp, profiles_bp, articles_bp, comments_bp, tags_bp):
        app.register_blueprint(blueprint, url_prefix='/api')

    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        print('数据库表已创建')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
