from app import create_app 

# create_app es una función definida en app/__init__.py que construye y configura la aplicación Flask
app = create_app()

if __name__ == "__main__":
    # debug=True hace que un Flask se reinicie automáticamente cada vez que cambia un fichero. Solo para desarrollo, nunca en producción.
    app.run(debug=True)
    