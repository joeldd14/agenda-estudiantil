from .database import db
from datetime import datetime, date

def today_str():
    return date.today().isoformat()

#--------------------------------------
#    TASKS - Tareas del usuario 
#--------------------------------------
class Task(db.Model):
    __tablename__ = "tasks"
    
    #primary_key = True -> columna única que identifica cada fila con autoincrement automático
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    #nullable = False -> CAMPO OBLIGATORIO, no puede estar vacío
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    
    # La fecha como string "YYYY-MM-DD"
    date = db.Column(db.String(10), nullable=False)
    
    #default = False -> si no se especifica, la tarea nace sin completar
    done = db.Column(db.Boolean, default=False)
    
    # IDs de categoría y asignatura las guardamos como texto
    category_id = db.Column(db.String(50), nullable=True)
    subject_id = db.Column(db.String(50), nullable=True)
    
    deadline = db.Column(db.String(10), nullable=True)
    note = db.Column(db.String(500), nullable=True)
    
    # "none", "daily", "weekly", "monthly"
    recurrence = db.Column(db.String(10), default="none")
    
    # "none", "high", "vhigh"
    priority = db.Column(db.String(10), default="none")
    
    time_start = db.Column(db.String(5), nullable=True)
    time_end = db.Column(db.String(5), nullable=True)
    
    # Convertir objeto a diccionario para poder enviarlo como JSON al frontend 
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "date": self.date,
            "done": self.done,
            "category_id": self.category_id,
            "subject_id": self.subject_id,
            "deadline": self.deadline,
            "note": self.note,
            "recurrence": self.recurrence,
            "priority": self.priority,
            "time_start": self.time_start,
            "time_end": self.time_end,
        }

#--------------------------------------
#       EXAMS - Exámenes
#--------------------------------------
class Exam(db.Model):
    __tablename__ = "exams"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    subject = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    
    # "parcial", "recuperación", "test", "laboratorio", ...
    type = db.Column(db.String(30), default="parcial")
    
    building = db.Column(db.String(100), nullable=True)
    room = db.Column(db.String(50), nullable=True)
    min_grade = db.Column(db.String(5), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    time_start = db.Column(db.String(5), nullable=True)
    time_end = db.Column(db.String(5), nullable=True)
    
    # Relación 1 a muchos con ExamGrade
    # backref="exam" añade exam.grades para acceder a las notas del examen
    # cascade="all, delete-orphan" -> si borras el examen se borran también todas sus notas automáticamente 
    grades = db.relationship(
        "ExamGrade", 
        backref="exam",
        cascade="all, delete-orphan",
        lazy=True #cargar en memoria automáticamente 
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "date": self.date,
            "type": self.type,
            "building": self.building,
            "room": self.room,
            "min_grade": self.min_grade,
            "notes": self.notes,
            "time_start": self.time_start,
            "time_end": self.time_end,
            # incluimos las notas anidadas dentro del examen  -> 1 Examen tiene muchas Notas
            "grades": [g.to_dict() for g in self.grades] #convertir notas a diccionarios
        }

#-----------------------------------------------------
#       EXAM GRADE - Notas de un examen concreto
#-----------------------------------------------------
class ExamGrade(db.Model):
    __tablename__ = "exam_grades"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    #ForeignKey -> esta columna apunta al id de la tabla exams
    # Si el examen se borra, esta fila también (por el cascade de arriba) 
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False) 
    
    label = db.Column(db.String(100), nullable=True)
    value = db.Column(db.String(100), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "label": self.label,
            "value": self.value
        }

#---------------------------------------------------------
#       TIMETABLE CLASS - Horario de clases semanal 
#---------------------------------------------------------
class TimetableClass(db.Model):
    __tablename__ = "timetable"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    subject = db.Column(db.String(50), nullable=False)
    
    day_of_week = db.Column(db.Integer, nullable=False)
    
    time_start = db.Column(db.String(5), nullable=False)
    time_end = db.Column(db.String(5), nullable=False)
    
    #"teoria", "laboratorio", "seminario", "otro"
    type = db.Column(db.String(20), default="teoria")
    
    building = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "day_of_week": self.day_of_week,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "type": self.type,
            "building": self.building,
            "room": self.room
        }


#---------------------------------------------------------
#       CANCELLED CLASS - Clase cancelada de un horario
#---------------------------------------------------------
class CancelledClass(db.Model):
    __tablename__ = "cancelled_classes"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    #Qué clase está cancelada
    class_id = db.Column(db.Integer, db.ForeignKey("timetable.id"), nullable=False)
    # La fecha en la que se canceló la clase
    date = db.Column(db.String(10), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "class_id": self.class_id,
            "date": self
        }

#-----------------------------------------------------------
#       DAY NOTE - Nota de texto libre por un día
#-----------------------------------------------------------
class DayNote(db.Model):
    __tablename__ = "day_notes"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    date = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "content": self.content
        }

#---------------------------------------------------------
#     DAY FLAG - Marcar un día como festivo o importante
#---------------------------------------------------------
class DayFlag(db.Model):
    __tablename__ = "day_flags"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    date = db.Column(db.String(10), nullable=False)
    is_holiday = db.Column(db.Boolean, nullable=False, default=False)
    is_important = db.Column(db.Boolean, nullable=False, default=False)
        
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "is_holiday": self.is_holiday,
            "is_important": self.is_important
        }

#-----------------------------------------------------------------------------------------------------
#     GRADE CONFIG - Configuración de ponderaciones y componentes de evaluación para cada materia
#-----------------------------------------------------------------------------------------------------
class GradeConfig(db.Model):
    __tablename__ = "grade_configs"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    subject_key = db.Column(db.String(50), nullable=False)
    
    label = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    min_grade = db.Column(db.String(5), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "subject_key": self.subject_key,
            "label": self.label,
            "weight": self.weight,
            "min_grade": self.min_grade
        }

#-----------------------------------------------------------------------------
#       GRADE VALUE - Nota introducida para una componente de evaluación
#-----------------------------------------------------------------------------
class GradeValue(db.Model):
    __tablename__ = "grade_values"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    subject_key = db.Column(db.String(50), nullable=False)
    
    #ForeignKey -> se vincula con el objeto GradeConfig
    config_id = db.Column(db.Integer, db.ForeignKey("grade_configs.id"), nullable=False)
    
    value = db.Column(db.String(100), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "subject_key": self.subject_key,
            "config_id": self.config_id,
            "value": self.value
        }

#-----------------------------------------------------------------------------------------------------
#    APP SETTINGS - Configuración global de la app (una sola fila con toda la configuración)
#-----------------------------------------------------------------------------------------------------
class AppSettings(db.Model):
    __tablename__ = "app_settings"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    #Guardamos categorías y asignaturas como JSON en texto
    #Es más simple que crear tablas separadas para listas  que el usuario personaliza libremente
    cats_json = db.Column(db.Text, nullable=True)
    subjects_json = db.Column(db.Text, nullable=True)
    
    accent = db.Column(db.String(10), default="#185FA5")
    dark_mode = db.Column(db.Boolean, default=False)
    font_size = db.Column(db.Integer, default=14)
    timetable_end = db.Column(db.String(7), nullable=True)
    
    def to_dict(self):
        #usamos json.loads para convertir de string a dict y a json para la app
        import json
        return {
            "id": self.id,
            "cats_json": json.loads(self.cats_json) if self.cats_json else [],
            "subjects_json": json.loads(self.subjects_json) if self.subjects_json else [],
            "accent": self.accent,
            "dark_mode": self.dark_mode,
            "font_size": self.font_size,
            "timetable_end": self.timetable_end
        }

#-------------------------------------------------------
#    USER - Usuarios de la app
#-------------------------------------------------------
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    
    #unique=True --> no pueden haber 2 usuarios con el mismo email
    email = db.Column(db.String(120), nullable=False, unique=True)
    
    #Guardamos la contraseña encriptada con bcrypt, nunca en texto plano
    #El hash de bcrypt siempre ocupa 60 caracteres
    password_hash = db.Column(db.String(60), nullable=False)
    
    #Fecha de creación 
    created_at = db.Column(db.String(10), default=today_str)
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at
        }
    