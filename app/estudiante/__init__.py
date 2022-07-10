import imp
from flask import Blueprint

estudiante_bp = Blueprint('estudiante', __name__, template_folder='templates')

from . import routes