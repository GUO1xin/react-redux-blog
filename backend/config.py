import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}:"
        f"{os.getenv('MYSQL_PASSWORD', '')}@"
        f"{os.getenv('MYSQL_HOST', '127.0.0.1')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DB', 'react_redux_blog')}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280}

    JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret-change-me')
    JWT_EXP_DAYS = int(os.getenv('JWT_EXP_DAYS', '30'))

    CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'http://localhost:4100')
