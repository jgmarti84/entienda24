from flask import Blueprint

tutor_bp = Blueprint('tutor', __name__, template_folder='templates')

from . import routes
