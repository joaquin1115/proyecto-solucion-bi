import os

class Config:

    # Carpeta temporal para uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads_tmp")

    # --------------------------------------------------------
    # 🔵 Variables de entorno — Azure PostgreSQL
    # --------------------------------------------------------
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    DB_NAME_PRACTITIONER = os.environ.get("DB_NAME_PRACTITIONER")
    DB_NAME_CI = os.environ.get("DB_NAME_CI")

    # --------------------------------------------------------
    # 🔵 Cadenas de conexión PostgreSQL
    # --------------------------------------------------------
    DB_CONN_STRINGS = {
        "practitioner": (
            f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME_PRACTITIONER} "
            f"user={DB_USER} password={DB_PASSWORD} sslmode=require"
        ),
        "continuous_integration": (
            f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME_CI} "
            f"user={DB_USER} password={DB_PASSWORD} sslmode=require"
        )
    }