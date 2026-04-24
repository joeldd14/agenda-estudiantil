from flask import Blueprint, request, jsonify
from ..database import db
from ..models import TimetableClass, CancelledClass

timetable_bp = Blueprint("timetable", __name__, url_prefix="/api/timetable")

# -- GET /api/timetable -------------------------
@timetable_bp.route("/", methods=["GET"])
def get_timetable():
    classes = TimetableClass.query.all()
    return jsonify([c.to_dict() for c in classes])


# -- POST /api/timetable ------------------------
@timetable_bp.route("/", methods=["POST"])
def create_timetable_entry():
    data = request.get_json()

    if not data or not data.get("subject") or not data.get("day"):
        return jsonify({"error": "La asignatura y el día son obligatorios"}), 400

    clss = TimetableEntry(
        subject=data.get("subject"),
        day=data.get("day"), # "monday", "tuesday", ...
        type=data.get("type"), # "class", "exam", "free"
        building=data.get("building"),
        room=data.get("room"),
        time_start=data.get("time_start"),
        time_end=data.get("time_end")
    )

    db.session.add(clss)
    db.session.commit()

    return jsonify(clss.to_dict()), 201


# -- DELETE /api/timetable/<id> -------------------
@timetable_bp.route("/<int:entry_id>", methods=["DELETE"])
def delete_timetable_entry(entry_id):
    clss = TimetableEntry.query.get_or_404(class_id)
    #Borramos también las cancelaciones de esta clase
    CancelledClass.query.filter_by(class_id=class_id).delete()
    db.session.delete(clss)
    db.session.commit()
    return jsonify({"message": "Clase eliminada correctamente"})

# -- GET /api/timetable/canceled ------------------------
# Devuelve todas las cancelaciones como diccionario {class_id_fecha: True}
@timetable_bp.route("/canceled", methods=["GET"])
def get_canceled_classes():
    cancelled = CancelledClass.query.all()
    result = {}
    for c in cancelled:
        key = f"{c.class_id}_{c.date}"
        result[key] = True #Para saber si esa clase esta cancelada
    return jsonify(result)

# -- POST /api/timetable/cancel ------------------------
# Activa o desactiva la cancelación de una clase en un día 
@timetable_bp.route("/cancel", methods=["POST"])
def cancel_class():
    data = request.get_json()
    class_id = data.get("class_id")
    date = data.get("date")
    if not class_id or not date:
        return jsonify({"error": "La clase y la fecha son obligatorias"}), 400
    
    #Buscamos si ya existe una cancelación para ese día
    existing = CancelledClass.query.filter_by(
        class_id = class_id,
        date = date
    ).first()
    
    if existing: 
        #Si existe -> la eliminamos (toggle off)
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"cancelled": False})
    else :
        #Si no existe -> la creamos (toggle on)
        cancelled = CancelledClass(
            class_id = class_id,
            date = date
        )
        db.session.add(cancelled)
        db.session.commit()
        return jsonify({"cancelled": True})
