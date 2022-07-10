from flask import render_template
from . import estudiante_bp

@estudiante_bp.route("/")
def estudiante():
    return render_template("estudiante.html")
