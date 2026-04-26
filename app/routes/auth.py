from flask import Blueprint, request, jsonify
from ..database import db
from ..models import User
from flask_jwt_extended import create_access_token
import bcrypt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ── POST /api/auth/register ──────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son obligatorios"}), 400

    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    # Comprobamos si el email ya existe
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Ya existe una cuenta con ese email"}), 409

    # Encriptamos la contraseña con bcrypt
    # El "12" es el coste del hash — más alto = más seguro pero más lento
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(12)
    ).decode("utf-8")

    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    # Generamos el token JWT con el id del usuario
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": user.to_dict()
    }), 201


# ── POST /api/auth/login ─────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son obligatorios"}), 400

    # Buscamos el usuario por email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Email o contraseña incorrectos"}), 401

    # Verificamos la contraseña con bcrypt
    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "Email o contraseña incorrectos"}), 401

    # Generamos el token JWT
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "user": user.to_dict()
    }), 200