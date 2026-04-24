from flask import Flask
from flask_cors import CORS
from .database import db

def create_app():
    #Crea la instancia de Flask
    #__name__ le dice a Flask dónde está la app para encotnrar ficheros estáticos y templates
    app = Flask(__name__)
    
    #Configuración de la base de datos
    #SQLite guarda todo en un fichero .db dentro de /instance 
    # /// significa "ruta relativa al proyecto"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agenda.db"
    
    #Desactiva un sistema de seguimiento de cambios de SQLAlchemy que consume memoria innecesariamente
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    #Inicializa CORS: permite que el Frontend React (que corre en otro puerto de desarrollo) hable con Flask 
    CORS(app)
    
    #Conecta SQLAlchemy con esta App Flask concreta
    db.init_app(app)
    
    #Registra los blueprints (conjuntos de rutas) 
    # (Los importamos aquí abajo para evitar bucles de importación)
    from .routes.tasks import tasks_bp
    from .routes.exams import exams_bp
    from .routes.timetable import timetable_bp
    from .routes.grades import grades_bp 
    from .routes.settings import settings_bp
    
    app.register_blueprint(tasks_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(settings_bp)
    
    # Crea todas las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()
    
    return app