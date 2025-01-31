from flask import Flask
# from shared.database import db_session, init_db
import os
from webapp import routes

def createApp():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        DATABASE_URL=os.getenv('DATABASE_URL')
    )
    
    app.register_blueprint(routes.bp)
    # # Initialize database
    # init_db()

    # # Register database session cleanup
    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db_session.remove()

    # # Register blueprints
    # from webapp.routes import bp
    # app.register_blueprint(bp)

    return app