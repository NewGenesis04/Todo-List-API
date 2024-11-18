from flask import Flask, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import LoginManager

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.secret_key = os.environ.get('SECRET_KEY')
    # comment by Tesla: why use the getenv dependency and the os.environ inbuilt in python to do thesame thing both can do

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(uid):
        from models import User
        return User.query.get(uid)

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Unauthorized access. Please log in."}), 401

    db.init_app(app)

    from routes import register_routes
    register_routes(app, db)

    migrate = Migrate(app, db)

    return app
