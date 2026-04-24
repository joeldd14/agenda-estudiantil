from flask import Blueprint, request, jsonify
from ..database import db
from ..models import Exam, ExamGrade

exams_bp = Blueprint("exams", __name__, url_prefix="/api/exams")

# -- GET /api/exams --------------------------
@exams_bp.route("/", methods=["GET"])
def get_exams():
    exams = Exam.query.all()
    return jsonify([e.to_dict() for e in exams])

# -- POST /api/exams -------------------------
@exams_bp.route("/", methods=["POST"])
def create_exam():
    data = request.get_json()
    
    if not data or not data.get("subject") or not data.get("date"):
        return jsonify({"error": "La asignatura y la fecha son obligatorias"}), 400
    
    exam = Exam(
        subject=data.get("subject"),
        date=data.get("date"),
        type=data.get("type"),
        building=data.get("building"),
        room=data.get("room"),
        min_grade=data.get("min_grade"),
        notes=data.get("notes"),
        time_start=data.get("time_start"),
        time_end=data.get("time_end")
    )
    
    db.session.add(exam)
    db.session.commit()
    
    #Si vienen notas junto con el examen, las creamos también
    for grade in data.get("grades", []):
        eg = ExamGrade(
            exam_id = exam.id,
            label = grade.get("label"),
            value = grade.get("value")
        )
        db.session.add(eg) #Las añade a la misma transacción
    
    #commit "graba" todo junto: el examen y todas las notas 
    db.session.commit()
    
    return jsonify(exam.to_dict()), 201

# -- PUT /api/exams/<id> -------------------------
@exams_bp.route("/<int:exam_id>", methods=["PUT"])
def update_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    data = request.get_json()

    if "subject" in data:       exam.subject = data["subject"]
    if "date" in data:          exam.date = data["date"]
    if "type" in data:          exam.type = data["type"]
    if "building" in data:      exam.building = data["building"]
    if "room" in data:          exam.room = data["room"]
    if "min_grade" in data:     exam.min_grade = data["min_grade"]
    if "notes" in data:         exam.notes = data["notes"]
    if "time_start" in data:    exam.time_start = data["time_start"]
    if "time_end" in data:      exam.time_end = data["time_end"]
    
    #Si vienen notas actualizadas, reemplazamos todas las antiguas (+ simple que actualizar 1 a 1)
    if "grades" in data:
        #1) Borramos las notas actuales del examen
        ExamenGrade.query.filter_by(exam_id=exam_id).delete()
        #2) Creamos las nuevas notas
        for grade in data["grades"]:
            eg = ExamenGrade(
                exam_id = exam_id,
                label = grade.get("label"),
                value = grade.get("value")
            )
            db.session.add(eg)
    
    db.session.commit()
    return jsonify(exam.to_dict())

# -- DELETE /api/exams/<id> -------------------------
@exams_bp.route("/<int:exam_id>", methods=["DELETE"])
def delete_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    return jsonify({"message": "Examen eliminado correctamente"})

