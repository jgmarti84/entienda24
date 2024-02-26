from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:testing@localhost:5432/miniblog'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres@localhost:5432/entienda24'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    login_manager.init_app(app)
    login_manager.login_view = "public.create"

    db.init_app(app)

    # Registro de los Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .public import public_bp
    app.register_blueprint(public_bp)

    from .tutor import tutor_bp
    app.register_blueprint(tutor_bp)

    from .student import student_bp
    app.register_blueprint(student_bp)

    with app.app_context():
        db.create_all()


    return app

app = create_app()
