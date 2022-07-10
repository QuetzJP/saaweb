import os
from flask import Flask, session
#from flask_mysqldb import MySQL
#from requests import Session
from requests import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from . import app_config


def create_app():
    #Creando app web
    app = Flask(__name__)
    app.config.from_object(app_config)
    app.config.from_mapping(
        SECRET_KEY='test'
    )
    Session()
    
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    #app.config['SECRET_KEY'] = 'asdfgh'
    
    #Inicializando DB
    #app.config['MYSQL_HOST']
    #app.config['MYSQL_USER']
    #app.config['MYSQL_PASSWORD']
    #app.config['MYSQL_DB']

    #mysql = MySQL(app)

    #Registro de los BP
    from .estudiante import estudiante_bp
    app.register_blueprint(estudiante_bp)
    
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
