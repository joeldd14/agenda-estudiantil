# Agenda Estudiantil

Aplicación web para gestión académica para estudiantes universitarios, desarrollada con Python (Flask) en el backend y React para el frontend.

## Funcionalidades

- **Gestión de tareas** - con categorías, prioridades, fechas límite y repetición
- **Gestión de tareas** — con categorías, prioridades, fechas límite y repetición
- **Exámenes** — seguimiento de próximos exámenes con aula, horario y notas
- **Horario universitario** — clases semanales con cancelaciones por día
- **Calculadora de notas** — ponderaciones por asignatura y nota mínima por componente
- **Estadísticas** — progreso por asignatura
- **Modo oscuro** y personalización de colores
- **Exportación/importación** de datos en JSON

## Tecnologías

| Capa          | Tecnología                             |
| ------------- | -------------------------------------- |
| Backend       | Python 3.13, Flask 3.1, SQLAlchemy 3.1 |
| Base de datos | SQLite                                 |
| Frontend      | React 18, CSS inline                   |
| API           | REST (JSON)                            |

## Instalación y uso local

### Requisitos

- Python 3.10 o superior
- pip

### Pasos

```bash
# 1. Clona el repositorio
git clone https://github.com/joeldd14/agenda-estudiantil.git
cd agenda-estudiantil

# 2. Instala las dependencias
pip install -r requirements.txt

# 3. Arranca el servidor
python run.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`

## Estructura del proyecto

```
agenda-python/
├── app/
│ ├── init.py # Application factory (patrón Flask estándar)
│ ├── database.py # Instancia de SQLAlchemy
│ ├── models.py # Modelos ORM: Task, Exam, TimetableClass...
│ └── routes/
│ ├── tasks.py # GET/POST/PUT/DELETE /api/tasks
│ ├── exams.py # GET/POST/PUT/DELETE /api/exams
│ ├── timetable.py # GET/POST/DELETE /api/timetable
│ ├── grades.py # GET/POST /api/grades
│ └── settings.py # GET/PUT /api/settings
├── instance/
│ └── agenda.db # Base de datos SQLite (generada automáticamente)
├── requirements.txt
└── run.py # Punto de entrada
```

## API REST

| Método | Endpoint          | Descripción               |
| ------ | ----------------- | ------------------------- |
| GET    | `/api/tasks/`     | Listar todas las tareas   |
| POST   | `/api/tasks/`     | Crear tarea               |
| PUT    | `/api/tasks/<id>` | Editar tarea              |
| DELETE | `/api/tasks/<id>` | Eliminar tarea            |
| GET    | `/api/exams/`     | Listar exámenes           |
| POST   | `/api/exams/`     | Crear examen              |
| GET    | `/api/timetable/` | Listar clases del horario |
| POST   | `/api/timetable/` | Añadir clase              |
| GET    | `/api/settings/`  | Obtener configuración     |
| PUT    | `/api/settings/`  | Actualizar configuración  |

## Autor

**Joel** — Estudiante de Ingeniería Informática  
[GitHub](https://github.com/joeldd14)

---

> Proyecto personal desarrollado para aprender desarrollo web con Python/Flask, arquitectura REST y gestión de bases de datos con SQLAlchemy.
