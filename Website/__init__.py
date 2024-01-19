from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_Name = "database.db"
database = f'sqlite:///{DB_Name}'

def create_app(database_uri=database):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'RMSPOPE'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from Website import models
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))
    
    return app

def create_database(app):
    if not path.exists('/Website/' + DB_Name):
        db.create_all(app=app)
        print('Created DataBase!')
