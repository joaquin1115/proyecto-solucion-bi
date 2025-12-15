# ============================================================
# 1. Importaciones
# ============================================================
import uuid
from flask import Blueprint, request, jsonify, current_app
from threading import Thread
from database import (
    get_dashboard_data, get_certification_summary, get_filter_options,
    get_certification_by_geography, get_summary_data,
    get_geographies_for_service_owner, get_services_for_service_owner,
    get_service_kpis, get_service_owner_chart_data, get_available_kpi_dates
)
from databricks_client import trigger_notebook_run

# Subida ADLS
from azure_storage import upload_csv_stream_to_datalake

api = Blueprint("api", __name__)


# ============================================================
# 2. Test API
# ============================================================
@api.route("/")
def index():
    return jsonify({"message": "API del Dashboard funcionando correctamente", "status": "ok"})


# ============================================================
# 3. Headers esperados por destino
# ============================================================
EXPECTED_HEADERS = {
    "practitioner": [
        'period_month','ug_name','uol1_name','uol2_name','servicel1_id',
        'servicel1_name','Nº fichas RFO','Nº SN2 con ficha RFO con status OK',
        'Nº SN2 con dependencias Consumer','Nº SN2 del tipo Aplicación no Hijo',
        'Número de features deployed válidas','Número de features deployed',
        'Valor de cumplimiento de objetivos en Op Model',
        'Servicios N2 con medición en el modelo objetivo del Op Model',
        'Vulnerab. de alto riesgo por cada mil líneas de códgio',
        'Vulnerab. de alto riesgo por cada mil líneas de códgio mes anterior',
        'Variación de la evolución de vulnerabilidades','Nº de vulnerabilidades high',
        'Nº de Lineas de código','Nº de vulnerabilidades high en el mes anterior',
        'Líneas de código en el mes anterior'
    ],
    "continuous_integration": [
        'period_month','ug_name','uol1_name','uol2_name','servicel1_id',
        'servicel1_name','issues_review_menor_7_dias','issues_en_revision_total',
        'historias_fix_version_deploy','cantidad_historias_deploy',
        'repos_activos_con_nomenclatura_estandar','total_repositorios_en_uso',
        'promedio_tiempo_aprobacion_pr','promedio_tamano_pr',
        'repos_gobernados_chimera_activos','promedio_tiempo_integracion',
        'promedio_tiempo_builds','pipelines_ejecuciones_exitosas',
        'pipelines_ejecuciones_totales','promedio_tiempo_reparacion_builds',
        'repos_sonarqube_ok_activos','repos_conectados_sonarqube',
        'items_pruebas_desplegados_xray','items_desplegados_totales'
    ]
}

TASK_STATUSES = {}


# ============================================================
# 4. Upload CSV directo a ADLS (sin archivos locales)
# ============================================================
@api.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename
    destination = request.form.get("destination")

    if not filename.lower().endswith(".csv"):
        return jsonify({"error": "El archivo debe ser .csv"}), 400

    if destination not in EXPECTED_HEADERS:
        return jsonify({"error": "Destino inválido."}), 400

    # -----------------------------------------
    # 1️⃣ Validar headers directo desde memoria
    # -----------------------------------------
    file.stream.seek(0)
    first_line = file.stream.readline().decode("utf-8")
    uploaded_headers = [h.replace("\ufeff", "").strip() for h in first_line.split(",")]

    if uploaded_headers != EXPECTED_HEADERS[destination]:
        return jsonify({
            "error": "Los encabezados del CSV NO coinciden.",
            "expected": EXPECTED_HEADERS[destination],
            "received": uploaded_headers
        }), 400

    # -----------------------------------------
    # 2️⃣ Subir directo al Data Lake
    # -----------------------------------------
    file.stream.seek(0)
    try:
        blob_path = upload_csv_stream_to_datalake(destination, filename, file.stream)
    except Exception as e:
        return jsonify({"error": f"Error subiendo a Data Lake: {str(e)}"}), 500

    # -----------------------------------------
    # 3️⃣ Lanzar pipeline Databricks en background
    # -----------------------------------------
    task_id = str(uuid.uuid4())
    TASK_STATUSES[task_id] = {
        "status": "procesando",
        "message": "Ejecutando pipeline..."
    }

    app = current_app._get_current_object()
    thread = Thread(
        target=process_background,
        args=(app, task_id, destination, filename, blob_path)
    )
    thread.start()

    return jsonify({"task_id": task_id}), 202


# ============================================================
# 5. Estado de procesamiento
# ============================================================
@api.route("/upload/status/<task_id>", methods=["GET"])
def upload_status(task_id):
    task = TASK_STATUSES.get(task_id)
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(task)


# ============================================================
# 6. Background – ejecutar Databricks
# ============================================================
def process_background(app, task_id, destination, filename, adls_path):
    with app.app_context():
        try:
            trigger_notebook_run(destination, adls_path)

            TASK_STATUSES[task_id] = {
                "status": "completado",
                "message": "Pipeline completado correctamente."
            }

        except Exception as e:
            TASK_STATUSES[task_id] = {
                "status": "error",
                "message": f"Error: {str(e)}"
            }


# ============================================================
# 7, 8 y 9 — ENDPOINTS DEL DASHBOARD (SIN CAMBIOS)
# ============================================================

@api.route("/data", methods=["GET"])
def data():
    args = request.args
    return jsonify(get_dashboard_data(
        maturity_level=args.get("maturity_level", "practitioner"),
        geografia=args.get("geografia", "todos"),
        service1_name=args.get("service1_name", "todos"),
        fecha=args.get("fecha", "todos"),
        page=args.get("page", 1, type=int),
        limit=args.get("limit", 10, type=int)
    ))

@api.route("/filters", methods=["GET"])
def filters():
    return jsonify(get_filter_options(
        request.args.get("maturity_level", "practitioner")
    ))

@api.route("/certification-summary", methods=["GET"])
def cert_summary():
    return jsonify(get_certification_summary(
        maturity_level=request.args.get("maturity_level", "practitioner"),
        geografia=request.args.get("geografia", "todos"),
        service1_name=request.args.get("service1_name", "todos"),
        fecha=request.args.get("fecha", "todos")
    ))

@api.route("/certification-by-geography", methods=["GET"])
def cert_by_geo():
    return jsonify(get_certification_by_geography(
        maturity_level=request.args.get("maturity_level", "practitioner"),
        service1_name=request.args.get("service1_name", "todos"),
        fecha=request.args.get("fecha", "todos")
    ))

@api.route("/summary", methods=["GET"])
def summary():
    args = request.args
    return jsonify(get_summary_data(
        maturity_level=args.get("maturity_level", "practitioner"),
        geografia=args.get("geografia", "todos"),
        service1_name=args.get("service1_name", "todos"),
        fecha=args.get("fecha", "todos")
    ))

@api.route("/service-owner/geographies", methods=["GET"])
def so_geografias():
    return jsonify(get_geographies_for_service_owner(
        request.args.get("maturity_level", "practitioner")
    ))

@api.route("/service-owner/services", methods=["GET"])
def so_services():
    return jsonify(get_services_for_service_owner(
        request.args.get("maturity_level", "practitioner"),
        request.args.get("geography", "todos")
    ))

@api.route("/service-owner/chart", methods=["GET"])
def so_chart():
    return jsonify(get_service_owner_chart_data(
        request.args.get("maturity_level", "practitioner"),
        request.args.get("geography", "todos"),
        request.args.get("service1_name", "todos"),
        request.args.get("metric", "adopcion_total_pct")
    ))

@api.route("/service-owner/service-kpis", methods=["GET"])
def so_kpis():
    return jsonify(get_service_kpis(
        request.args.get("maturity_level", "practitioner"),
        request.args.get("geography", "todos"),
        request.args.get("service1_name", "todos"),
        request.args.get("date", None)
    ))

@api.route("/service-owner/kpi-dates", methods=["GET"])
def so_kpi_dates():
    return jsonify(get_available_kpi_dates(
        request.args.get("maturity_level", "practitioner"),
        request.args.get("geography", "todos"),
        request.args.get("service1_name", "todos")
    ))