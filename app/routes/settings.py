from flask import Blueprint, request, jsonify
from ..database import db
from ..models import AppSettings, DayNote, DayFlag
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")

#Función auxiliar que obtiene la configuración o la crea con valores por defecto si no existe todavía
def get_or_create_settings(user_id):
    settings = AppSettings.query.first()
    if not settings:
        #1ª vez que arranca la app -> creamos configuración por defecto
        settings = AppSettings(
            user_id = user_id,
            cats_json=json.dumps([
                {"id": "trabajo", "label": "Trabajo", "color": "#185FA5"},
                {"id": "personal", "label": "Personal", "color": "#0F6E56"},
                {"id": "salud", "label": "Salud", "color": "#993556"},
                {"id": "futbol", "label": "Fútbol", "color": "#15803d"},
                {"id": "otro", "label": "Otro", "color": "#5F5E5A"},
            ]),
            subjects_json=json.dumps([
                {"id": "calc", "label": "Cálculo", "color": "#7c3aed"},
                {"id": "prog", "label": "Programación", "color": "#0f766e"},
                {"id": "redes", "label": "Redes", "color": "#c2410c"},
                {"id": "so", "label": "Sistemas Op.", "color": "#15803d"},
            ]),
            accent="#185FA5",
            dark_mode=False,
            font_size=14,
        )
        db.session.add(settings)
        db.session.commit()
    return settings

# -- GET /api/settings -------------------------
@settings_bp.route("/", methods=["GET"])
@jwt_required()
def get_settings():
    user_id = get_jwt_identity()
    settings = get_or_create_settings(user_id)
    return jsonify(settings.to_dict())

# -- PUT /api/settings --------------------------
# Actualiza cualquier campo de la configuración
@settings_bp.route("/", methods=["PUT"])
@jwt_required()
def update_settings():
    user_id = get_jwt_identity()
    settings = get_or_create_settings(user_id)
    data = request.get_json()
    
    #json.dumps convierte la lista Python a texto JSON para guardarlo 
    if "cats" in data:
        settings.cats_json = json.dumps(data["cats"])
    if "subjects" in data:
        settings.subjects_json = json.dumps(data["subjects"])
    if "accent" in data:
        settings.accent = data["accent"]
    if "dark_mode" in data:
        settings.dark_mode = data["dark_mode"]
    if "font_size" in data:
        settings.font_size = data["font_size"]
    if "timetable_end" in data:
        settings.timetable_end = data["timetable_end"]
    
    db.session.commit()
    return jsonify(settings.to_dict())

# -- GET /api/settings/notes ----------------------------------
#Devuelve todas las notas de días como diccionario {"2025-04-24": "texto...", "2025-04-25": "otro texto..."}
@settings_bp.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = get_jwt_identity()
    notes = DayNote.query.filter_by(user_id=user_id).all()
    return jsonify({note.date:note.text for note in notes})

# -- PUT /api/settings/notes/<date> --------------------------
# Guarda o actualiza la nota de un día concreto
@settings_bp.route("/notes/<date>", methods=["PUT"])
@jwt_required()
def save_note(date):
    user_id = get_jwt_identity()
    data = request.get_json()
    content = data.get("content", "")
    
    existing = DayNote.query.filter_by(date=date, user_id=user_id).first()
    if existing:
        existing.content = content
    else:
        note = DayNote(user_id=user_id, date=date, content=content)
        db.session.add(note)
    
    db.session.commit()
    return jsonify({"date": date, "content": content})

# -- GET /api/settings/flags ----------------------------------
# Devuelve festivos e importantes como dos diccionarios separados
@settings_bp.route("/flags", methods=["GET"])
@jwt_required()
def get_flags():
    user_id = get_jwt_identity()
    flags = DayFlag.query.filter_by(user_id=user_id).all()
    important = {}
    holidays = {}
    for f in flags:
        if f.is_important:
            important[f.date] = True
        if f.is_holiday:
            holidays[f.date] = True
    return jsonify({"important": important, "holidays": holidays})

# -- PUT /api/settings/flags/<date> --------------------------
# Actualiza los flags de un día concreto 
@settings_bp.route("/flags/<date>", methods=["PUT"])
@jwt_required()
def save_flag(date):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    existing = DayFlag.query.filter_by(date=date, user_id=user_id).first()
    if existing:
        existing.is_important = data.get("isImportant", existing.is_important)
        existing.is_holiday = data.get("isHoliday", existing.is_holiday)
    else:
        flag = DayFlag(
            user_id=user_id,
            date=date,
            is_important = data.get("isImportant", False),
            is_holiday = data.get("isHoliday", False),
        )
        db.session.add(flag)
    
    db.session.commit()
    return jsonify({"message": "Flag guardado correctamente"})