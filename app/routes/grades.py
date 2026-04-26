from flask import Blueprint, request, jsonify
from ..database import db
from ..models import GradeConfig, GradeValue
from flask_jwt_extended import jwt_required, get_jwt_identity

grades_bp = Blueprint("grades", __name__, url_prefix="/api/grades")

# -- GET /api/grades/config --------------------------
# Devuelve todas las configuraciones agrupadas por asignatura {calc: [{id, label, weigth, minGrade}], prog: [...]}
@grades_bp.route("/config", methods=["GET"])
@jwt_required()
def get_configs():
    user_id = get_jwt_identity()
    configs = GradeConfig.query.filter_by(user_id=user_id).all()
    result = {}
    for c in configs:
        #Si la asignatura no tiene la lista todavía -> la creamos
        if c.subject_key not in result:
            result[c.subject_key] = []
        result[c.subject_key].append(c.to_dict())
    return jsonify(result)

# -- POST /api/grades/config --------------------------
# Guarda la configuración completa de una asignatura
# Reemplaza todas las componentes existentes de esa asignatura
@grades_bp.route("/config", methods=["POST"])
@jwt_required()
def save_config():
    user_id = get_jwt_identity()
    data = request.get_json()
    subject_key = data.get("subject_key")
    components = data.get("components", [])
    if not subject_key:
        return jsonify({"error": "Asignatura obligatoria"}), 400
    
    #1) Borramos las componentes antiguas de esta asignatura
    GradeConfig.query.filter_by(subject_key=subject_key, user_id=user_id).delete()
    #2) Creamos las nuevas componentes
    for c in components:
        gc = GradeConfig(
            user_id = user_id,
            subject_key = subject_key,
            label = c.get("label"),
            weight = float(c.get("weight",0)),
            min_grade = c.get("minGrade")
        )
        db.session.add(gc)
    
    db.session.commit()
    
    #Devolvemos la nueva configuración de esta asignatura
    new_configs = GradeConfig.query.filter_by(subject_key=subject_key, user_id=user_id).all()
    return jsonify([c.to_dict() for c in new_configs]), 201

# -- GET /api/grades/values --------------------------
# Devuelve todas las notas existentes agrupadas por asignatura
@grades_bp.route("/values", methods=["GET"])
@jwt_required()
def get_grade_values():
    user_id = get_jwt_identity()
    values = GradeValue.query.filter_by(user_id=user_id).all()
    result = {}
    for v in values:
        if v.subject_key not in result:
            result[v.subject_key] = []
        result[v.subject_key][str(v.config_id)] = v.value
    return jsonify(result)


# -- POST /api/grades/values -------------------------
# Guarda o actualiza los valores de las notas de una componente concreta (pueden venir en cualquier momento)
@grades_bp.route("/values", methods=["POST"])
@jwt_required()
def save_grade_values():
    user_id = get_jwt_identity()
    data = request.get_json()
    subject_key = data.get("subject_key")
    config_id = data.get("config_id")
    value = data.get("value")
    
    if not subject_key or not config_id:
        return jsonify({"error": "Asignatura y componente obligatorios"}), 400
    
    #Buscamos si ya existe un valor para esa componente
    existing = GradeValue.query.filter_by(
        user_id = user_id,
        subject_key = subject_key,
        config_id = config_id
    ).first()
    
    if existing:
        #Si existe -> la actualizamos
        existing.value = value
    else:
        #Si no existe -> la creamos
        gv = GradeValue(
            user_id = user_id,
            subject_key = subject_key,
            config_id = config_id,
            value = value
        )
        db.session.add(gv)
    
    db.session.commit()
    return jsonify({"message": "Nota guardada correctamente"}), 200