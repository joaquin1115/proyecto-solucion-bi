import os
import logging
from azure.storage.filedatalake import DataLakeServiceClient

# =============================================
# CONFIGURACIÓN LOGS    
# =============================================
logging.basicConfig(
    level=logging.INFO,
    format="🔵 [ADLS] %(message)s"
)

AZURE_CONN_STR = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

if not AZURE_CONN_STR:
    raise RuntimeError("❌ Falta la variable AZURE_STORAGE_CONNECTION_STRING en el entorno.")

logging.info("Conexión encontrada. Inicializando cliente ADLS Gen2...")

# Cliente ADLS Gen2 REAL (DFS)
datalake = DataLakeServiceClient.from_connection_string(AZURE_CONN_STR)

CONTAINER_NAME = "bronze"


def upload_csv_stream_to_datalake(destination: str, filename: str, stream):
    """
    Sube a ADLS Gen2 con LOGS detallados.
    Borra toda la carpeta de destino antes de subir.
    """

    logging.info(f"📥 Recibido archivo: {filename}")
    logging.info(f"📌 Destino solicitado: {destination}")

    # Carpetas REALES
    if destination == "practitioner":
        folder = "data_sucia/data_sucia_practitioner"
    else:
        folder = "data_sucia/data_sucia_continuous_integration"

    logging.info(f"📁 Carpeta destino en ADLS: {folder}")

    fs = datalake.get_file_system_client(CONTAINER_NAME)

    # =============================================
    # 1️⃣ BORRAR TODO EL CONTENIDO EXISTENTE
    # =============================================
    logging.info("🗑 Intentando borrar archivos previos...")

    deleted_count = 0

    try:
        for path in fs.get_paths(path=folder):
            logging.info(f"   - Eliminando: {path.name}")
            fs.delete_file(path.name)
            deleted_count += 1
    except Exception as e:
        logging.info(f"⚠ No existía la carpeta o hubo un error menor: {str(e)}")

    logging.info(f"✔ Archivos eliminados: {deleted_count}")

    # =============================================
    # 2️⃣ SUBIR NUEVO ARCHIVO
    # =============================================
    blob_path = f"{folder}/{filename}"
    logging.info(f"⬆️ Subiendo nuevo archivo a: {blob_path}")

    stream.seek(0)

    directory = fs.get_directory_client(folder)
    file_client = directory.get_file_client(filename)

    try:
        file_client.upload_data(stream, overwrite=True)
        logging.info("✔ Subida exitosa al Data Lake.")
    except Exception as e:
        logging.error(f"❌ Error subiendo archivo: {str(e)}")
        raise

    # =============================================
    # 3️⃣ RUTA ABFSS PARA DATABRICKS
    # =============================================
    account = datalake.account_name
    final_path = f"abfss://{CONTAINER_NAME}@{account}.dfs.core.windows.net/{blob_path}"

    logging.info(f"📡 Ruta ADLS entregada a Databricks:")
    logging.info(f"   → {final_path}")

    return final_path
