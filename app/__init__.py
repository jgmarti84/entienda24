from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
# import flask_monitoringdashboard as dashboard
import config
import pytz


# ba_tz = timezone('America/Argentina/Buenos_Aires')
import os
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()

login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    login_manager.init_app(app)
    login_manager.login_view = "public.create_account"

    db.init_app(app)
    migrate = Migrate(app, db)
    # dashboard.bind(app)

    # Registro de los Blueprints
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .public import public_bp
    app.register_blueprint(public_bp)

    from .tutor import tutor_bp
    app.register_blueprint(tutor_bp)

    from .student import student_bp
    app.register_blueprint(student_bp)

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            # current_user.user.updated_at = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
            current_user.user.updated_at = datetime.now()
            db.session.commit()

    with app.app_context():
        db.create_all()

    # error logging!
    if not os.path.exists(config.LOGGING_DIRECTORY):
        os.makedirs(config.LOGGING_DIRECTORY)
    # file_handler = RotatingFileHandler(
    #     f"{config.LOGGING_DIRECTORY}/entiendayaprenda.log",
    #     maxBytes=10240,
    #     backupCount=10
    # )
    # file_handler.setFormatter(
    #     logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    # )
    # file_handler.setLevel(logging.INFO)
    # app.logger.addHandler(file_handler)
    #
    # app.logger.setLevel(logging.INFO)
    # app.logger.info('Entienda y Aprenda startup')

    return app


app = create_app()
