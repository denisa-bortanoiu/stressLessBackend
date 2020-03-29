import connexion

from .extensions import db, migrate


def create_app():
    swagger_options = {
        'swagger_url': 'docs'
    }
    app_conn = connexion.FlaskApp(__name__, options=swagger_options)
    app_conn.add_api('openapi.yaml')

    settings = {
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://stress:stress@mariadb:3306/stress',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_recycle': 3600,
            'pool_pre_ping': True
        }
    }
    app = app_conn.app
    app.config.from_mapping(settings)
    db.init_app(app)
    db.app = app
    migrate.init_app(app, db)

    return app


app = create_app()
