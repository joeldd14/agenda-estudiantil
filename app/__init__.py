from flask import Flask, send_from_directory
from flask_cors import CORS
from .database import db
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
load_dotenv()

def create_app():
    #Crea la instancia de Flask
    #__name__ le dice a Flask dónde está la app para encotnrar ficheros estáticos y templates
    app = Flask(__name__)
    
    #Configuración de la BASE DE DATOS (en local usa SQLite y en producción usa PostgreSQL)
    database_url = os.getenv("DATABASE_URL", "sqlite:///agenda.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    #Desactiva un sistema de seguimiento de cambios de SQLAlchemy que consume memoria innecesariamente
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    #Configuración de JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback-solo desarrollo")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    
    #Inicializa CORS: permite que el Frontend React (que corre en otro puerto de desarrollo) hable con Flask 
    CORS(app)
    
    #Conecta SQLAlchemy con esta App Flask concreta
    db.init_app(app)
    
    #Inicializa JWT
    JWTManager(app)
    
    #Registra los blueprints (conjuntos de rutas) 
    # (Los importamos aquí abajo para evitar bucles de importación)
    from .routes.tasks import tasks_bp
    from .routes.exams import exams_bp
    from .routes.timetable import timetable_bp
    from .routes.grades import grades_bp 
    from .routes.settings import settings_bp
    from .routes.auth import auth_bp
    
    app.register_blueprint(tasks_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)
    
    @app.route("/")
    @app.route("/index.html")
    def index():
    # Sirve el index.html desde la carpeta frontend/
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
        return send_from_directory(frontend_path, "index.html")

    @app.route("/<path:filename>")
    def frontend_files(filename):
        # Si la ruta empieza por "api/", no la interceptamos
        if filename.startswith("api/"):
            from flask import abort
            abort(404)
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
        return send_from_directory(frontend_path, filename)
    
    # Crea todas las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()
    
    return app