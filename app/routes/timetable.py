from flask import Blueprint, request, jsonify
from ..database import db
from ..models import TimetableClass, CancelledClass
from flask_jwt_extended import jwt_required, get_jwt_identity

timetable_bp = Blueprint("timetable", __name__, url_prefix="/api/timetable")


# ── GET /api/timetable/ ──────────────────────────────────
@timetable_bp.route("/", methods=["GET"])
@jwt_required()
def get_timetable():
    user_id = get_jwt_identity()
    classes = TimetableClass.query.filter_by(user_id=user_id).all()
    return jsonify([c.to_dict() for c in classes])


# ── POST /api/timetable/ ─────────────────────────────────
@timetable_bp.route("/", methods=["POST"])
@jwt_required()
def create_class():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get("subject"):
        return jsonify({"error": "La asignatura es obligatoria"}), 400

    cls = TimetableClass(
        user_id=user_id,
        subject=data["subject"],
        day_of_week=data.get("dayOfWeek", 0),
        start_time=data.get("startTime", "09:00"),
        end_time=data.get("endTime", "10:00"),
        type=data.get("type", "teoria"),
        building=data.get("building"),
        room=data.get("room"),
    )
    db.session.add(cls)
    db.session.commit()
    return jsonify(cls.to_dict()), 201


# ── GET /api/timetable/cancelled ─────────────────────────
# OJO: esta ruta va ANTES que /<int:class_id>
@timetable_bp.route("/cancelled", methods=["GET"])
@jwt_required()
def get_cancelled():
    user_id = get_jwt_identity()
    user_class_ids = [c.id for c in TimetableClass.query.filter_by(user_id=user_id).all()]
    cancelled = CancelledClass.query.filter(CancelledClass.class_id.in_(user_class_ids)).all()
    result = {}
    for c in cancelled:
        key = f"{c.class_id}_{c.date}"
        result[key] = True
    return jsonify(result)


# ── POST /api/timetable/cancelled/toggle ─────────────────
@timetable_bp.route("/cancelled/toggle", methods=["POST"])
@jwt_required()
def toggle_cancelled():
    data = request.get_json()
    class_id = data.get("classId")
    date = data.get("date")

    if not class_id or not date:
        return jsonify({"error": "classId y date son obligatorios"}), 400

    existing = CancelledClass.query.filter_by(
        class_id=class_id,
        date=date
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"cancelled": False})
    else:
        cancelled = CancelledClass(class_id=class_id, date=date)
        db.session.add(cancelled)
        db.session.commit()
        return jsonify({"cancelled": True})


# ── DELETE /api/timetable/<id> ───────────────────────────
# OJO: esta ruta va DESPUÉS de /cancelled y /cancelled/toggle
@timetable_bp.route("/<int:class_id>", methods=["DELETE"])
@jwt_required()
def delete_class(class_id):
    user_id = get_jwt_identity()
    cls = TimetableClass.query.filter_by(id=class_id, user_id=user_id).first_or_404()
    CancelledClass.query.filter_by(class_id=class_id).delete()
    db.session.delete(cls)
    db.session.commit()
    return jsonify({"message": "Clase eliminada"}), 200