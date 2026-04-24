from flask import Blueprint, request, jsonify
from ..database import db
from ..models import Task

#Blueprint es una forma de agrupar rutas relacionadas 
# "tasks" es el nombre interno, url_prefix añade /api/tasks a todas las rutas de este fichero automáticamente
tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

#-- GET /api/tasks --------------------------
#Devuelve todas las tareas 
@tasks_bp.route("/", methods=["GET"])
def get_tasks():
    tasks = Task.query.all() #equivale a SELECT * FROM tasks
    #to_dict() convierte cada objeto Task a diccionario
    #jsonify() convierte el diccionario a JSON para enviarlo
    return jsonify([t.to_dict() for t in tasks])

#-- POST /api/tasks --------------------------
#Crea una tarea nueva
#El frontend manda los datos en el body de la petición como JSON 
@tasks_bp.route("/", methods=["POST"])
def create_task():
    data = request.get_json() #Lee el JSON que manda el frontend
    
    #Validación básica: el título es obligatorio
    if not data or not data.get("title"):
        return jsonify({"error": "El título es obligatorio"}), 400

    task = Task(
        title=data.get("title"),
        description=data.get("description"),  #.get() devuelve None si no existe
        date=data.get("date"),
        done=data.get("done", False),
        category_id=data.get("category_id"),
        subject_id=data.get("subject_id"),
        deadline=data.get("deadline"),
        note=data.get("note"),
        recurrence=data.get("recurrence", "none"),
        priority=data.get("priority", "none"),
        time_start=data.get("time_start"),
        time_end=data.get("time_end"),
    )
    
    db.session.add(task) # Prepara la inserción
    db.session.commit() # Ejecuta el INSERT en SQLite
    
    return jsonify(task.to_dict()), 201 #201 Created

#-- PUT /api/tasks/<int:id> --------------------------
#Edita una tarea existente
#<int:task_id> captura el número de la URL: /api/tasks/5
@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    #get_or_404 busca la tarea y si no existe devuelve el error 404
    task = Task.query.get_or_404(task_id)
    data = request.get_json() #lee el JSON que manda el frontend
    
    #Solo actualizamos los campos que vienen en la petición 
    if "title" in data:    task.title = data["title"]
    if "desc" in data:     task.desc = data["desc"]
    if "date" in data:     task.date = data["date"]
    if "done" in data:     task.done = data["done"]
    if "cat" in data:      task.cat = data["cat"]
    if "subject" in data:  task.subject = data["subject"]
    if "deadline" in data: task.deadline = data["deadline"]
    if "note" in data:     task.note = data["note"]
    if "recur" in data:    task.recur = data["recur"]
    if "priority" in data: task.priority = data["priority"]
    if "timeStart" in data: task.time_start = data["timeStart"]
    if "timeEnd" in data:   task.time_end = data["timeEnd"]
    
    db.session.commit() #Ejecuta el UPDATE en SQLite
    return jsonify(task.to_dict())

#-- DELETE /api/tasks/<id> --------------------------
@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id) #busca la tarea 
    db.session.delete(task) #prepara el DELETE
    db.session.commit() #ejecuta el DELETE en SQLite 
    return jsonify({"message": "Tarea eliminada correctamente"}), 200
