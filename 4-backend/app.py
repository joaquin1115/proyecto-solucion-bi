from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)

    # CORS para React
    CORS(app)

    # Cargar configuración
    app.config.from_object("config.Config")

    # Crear carpeta temporal
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Rutas
    from routes import api
    app.register_blueprint(api, url_prefix="/api")

    # DB teardown
    import database
    app.teardown_appcontext(database.close_db)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, extra_files=[])