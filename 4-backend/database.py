# ============================================================
# 1. Importar librerías
# ============================================================
from datetime import datetime
import psycopg2
import psycopg2.extras
from config import Config
from flask import g


# ============================================================
# 2. Conexión a la base de datos
# ============================================================
def get_db(maturity_level='practitioner'):
    if 'db_connections' not in g:
        g.db_connections = {}

    if maturity_level not in g.db_connections:
        conn_string = Config.DB_CONN_STRINGS.get(maturity_level)
        if not conn_string:
            raise ValueError(f"No se encontró cadena de conexión para {maturity_level}")
        g.db_connections[maturity_level] = psycopg2.connect(conn_string)
    
    return g.db_connections[maturity_level]


def close_db(e=None):
    connections = g.pop('db_connections', {})
    for conn in connections.values():
        conn.close()


# ============================================================
# 3. Construcción dinámica de filtros
# ============================================================
def _build_where_clause(**filters):
    where = []
    params = []

    mapping = {
        'geografia': "geografia = %s",
        'service1_name': "service1_name = %s",
        'fecha': "fecha = %s"
    }

    for key, value in filters.items():
        if value and value != "todos" and key in mapping:
            where.append(mapping[key])
            params.append(value)

    sql = ""
    if where:
        sql = "WHERE " + " AND ".join(where)

    return sql, params


# ============================================================
# 4. Obtener nombre de vista según nivel
# ============================================================
def _get_view_for_level(maturity_level):
    if maturity_level == "continuous_integration":
        return "public.vw_ci_kpis"
    return "public.vw_practitioner_kpis"


# ============================================================
# 5. REFRESCAR VISTAS (NO HACE NADA, SOLO POR COMPATIBILIDAD)
# ============================================================
def refresh_view(maturity_level='practitioner'):
    """
    En la arquitectura actual Databricks escribe directamente en las tablas
    base que alimentan las vistas public.vw_practitioner_kpis y public.vw_ci_kpis,
    por lo que no es necesario recrear ni refrescar vistas desde el backend.
    """
    return {"message": "Refresco de vista no requerido; las vistas se actualizan con las tablas base."}


# ============================================================
# 6. DATASET PRINCIPAL
# ============================================================
def get_dashboard_data(maturity_level='practitioner', page=1, limit=10,
                       geografia='todos', service1_name='todos', fecha='todos'):

    view = _get_view_for_level(maturity_level)
    where_sql, params = _build_where_clause(
        geografia=geografia, service1_name=service1_name, fecha=fecha
    )

    # Columnas según nivel
    if maturity_level == 'continuous_integration':
        cols = """
            TO_CHAR(fecha, 'YYYY-MM-DD') as fecha, geografia, service1_name,
            analisis_review_7dias_pct, historias_fix_version_pct, repos_nomenclatura_pct,
            aprobacion_pr_pct, tamano_pr_pct, repos_chimera_pct, tiempo_integracion_pct,
            tiempo_construcciones_pct, construcciones_correctas_pct,
            tiempo_arreglar_construcciones_pct, calidad_codigo_pct, items_pruebas_xray_pct,
            adopcion_total_pct
        """
    else:
        cols = """
            TO_CHAR(fecha, 'YYYY-MM-DD') as fecha, geografia, service1_name,
            rfo_ok_pct, dep_pct, adopcion_sn2_pct, calidad_features_pct, seguridad_pct,
            adopcion_total_pct
        """

    query_count = f"SELECT COUNT(*) FROM {view} {where_sql};"
    query_data = f"""
        SELECT {cols}
        FROM {view}
        {where_sql}
        ORDER BY fecha DESC, geografia, service1_name
        LIMIT %s OFFSET %s;
    """

    conn = get_db(maturity_level)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

            cur.execute(query_count, params)
            total = cur.fetchone()[0]

            cur.execute(query_data, params + [limit, (page - 1) * limit])
            data = [dict(row) for row in cur.fetchall()]

        return {"data": data, "totalCount": total}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 7. RESUMEN CERTIFICACIÓN
# ============================================================
def get_certification_summary(maturity_level='practitioner',
                              geografia='todos', service1_name='todos', fecha='todos'):

    view = _get_view_for_level(maturity_level)
    where_sql, params = _build_where_clause(
        geografia=geografia, service1_name=service1_name, fecha=fecha
    )

    q = f"""
        SELECT
            COUNT(CASE WHEN adopcion_total_pct >= 90 THEN 1 END) AS "LEVEL 3",
            COUNT(CASE WHEN adopcion_total_pct >= 80 AND adopcion_total_pct < 90 THEN 1 END) AS "LEVEL 2",
            COUNT(CASE WHEN adopcion_total_pct >= 70 AND adopcion_total_pct < 80 THEN 1 END) AS "LEVEL 1",
            COUNT(CASE WHEN adopcion_total_pct < 70 THEN 1 END) AS "no certificado"
        FROM {view}
        {where_sql};
    """

    conn = get_db(maturity_level)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(q, params)
            row = cur.fetchone()
            return {k: int(v) for k, v in row.items()}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 8. CERTIFICACIÓN POR GEOGRAFÍA
# ============================================================
def get_certification_by_geography(maturity_level='practitioner',
                                   service1_name='todos', fecha='todos'):

    view = _get_view_for_level(maturity_level)

    where_sql, params = _build_where_clause(service1_name=service1_name, fecha=fecha)

    q = f"""
        SELECT
            geografia,
            COUNT(CASE WHEN adopcion_total_pct >= 90 THEN 1 END) AS "LEVEL 3",
            COUNT(CASE WHEN adopcion_total_pct >= 80 AND adopcion_total_pct < 90 THEN 1 END) AS "LEVEL 2",
            COUNT(CASE WHEN adopcion_total_pct >= 70 AND adopcion_total_pct < 80 THEN 1 END) AS "LEVEL 1",
            COUNT(CASE WHEN adopcion_total_pct < 70 THEN 1 END) AS "no certificado"
        FROM {view}
        {where_sql}
        GROUP BY geografia
        ORDER BY geografia;
    """

    conn = get_db(maturity_level)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(q, params)
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 9. OPCIONES DE FILTROS
# ============================================================
def get_filter_options(maturity_level='practitioner'):

    view = _get_view_for_level(maturity_level)
    conn = get_db(maturity_level)

    try:
        with conn.cursor() as cur:

            cur.execute(f"""
                SELECT DISTINCT geografia
                FROM {view}
                WHERE geografia IS NOT NULL
                ORDER BY geografia;
            """)
            geografias = [r[0] for r in cur.fetchall()]

            cur.execute(f"""
                SELECT DISTINCT service1_name
                FROM {view}
                WHERE service1_name IS NOT NULL
                ORDER BY service1_name;
            """)
            services = [r[0] for r in cur.fetchall()]

            cur.execute(f"""
                SELECT DISTINCT TO_CHAR(fecha, 'YYYY-MM-DD') AS fecha_str
                FROM {view}
                WHERE fecha IS NOT NULL
                ORDER BY fecha_str DESC;
            """)
            fechas = [r[0] for r in cur.fetchall()]

        return {"geografias": geografias, "services": services, "fechas": fechas}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 10. RESUMEN DE DATOS
# ============================================================
def get_summary_data(maturity_level='practitioner',
                     geografia='todos', service1_name='todos', fecha='todos'):

    view = _get_view_for_level(maturity_level)
    where_sql, params = _build_where_clause(
        geografia=geografia, service1_name=service1_name, fecha=fecha
    )

    q = f"""
        SELECT
            COUNT(*) AS total_count,
            AVG(adopcion_total_pct) AS avg_adoption,
            COUNT(DISTINCT geografia) AS geographies_count
        FROM {view}
        {where_sql};
    """

    conn = get_db(maturity_level)

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(q, params)
            r = cur.fetchone()

            return {
                "totalCount": int(r['total_count'] or 0),
                "avg_adoption": float(r['avg_adoption'] or 0),
                "geographies_count": int(r['geographies_count'] or 0)
            }

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 11. GEOGRAFÍAS PARA SERVICE OWNER
# ============================================================
def get_geographies_for_service_owner(maturity_level='practitioner'):

    view = _get_view_for_level(maturity_level)
    conn = get_db(maturity_level)

    q = f"SELECT DISTINCT geografia FROM {view} WHERE geografia IS NOT NULL ORDER BY geografia;"

    try:
        with conn.cursor() as cur:
            cur.execute(q)
            return {"geografias": [r[0] for r in cur.fetchall()]}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 12. SERVICIOS PARA SERVICE OWNER
# ============================================================
def get_services_for_service_owner(maturity_level='practitioner', geography='todos'):

    view = _get_view_for_level(maturity_level)
    conn = get_db(maturity_level)

    where = ["service1_name IS NOT NULL"]
    params = []

    if geography != "todos":
        where.append("geografia = %s")
        params.append(geography)

    where_sql = "WHERE " + " AND ".join(where)

    q = f"""
        SELECT DISTINCT service1_name
        FROM {view}
        {where_sql}
        ORDER BY service1_name;
    """

    try:
        with conn.cursor() as cur:
            cur.execute(q, params)
            return {"services": [r[0] for r in cur.fetchall()]}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 13. SERVICE OWNER – Datos Línea
# ============================================================
def get_service_owner_chart_data(maturity_level='practitioner',
                                 geography='todos',
                                 service1_name='todos',
                                 metric='adopcion_total_pct'):

    if maturity_level == 'practitioner':
        allowed = [
            'rfo_ok_pct', 'dep_pct', 'adopcion_sn2_pct',
            'calidad_features_pct', 'seguridad_pct', 'adopcion_total_pct'
        ]
    else:
        allowed = [
            'analisis_review_7dias_pct', 'historias_fix_version_pct', 'repos_nomenclatura_pct',
            'aprobacion_pr_pct', 'tamano_pr_pct', 'repos_chimera_pct', 'tiempo_integracion_pct',
            'tiempo_construcciones_pct', 'construcciones_correctas_pct',
            'tiempo_arreglar_construcciones_pct', 'calidad_codigo_pct',
            'items_pruebas_xray_pct', 'adopcion_total_pct'
        ]

    if metric not in allowed:
        return {"error": "Métrica no válida"}

    view = _get_view_for_level(maturity_level)
    where = [f"{metric} IS NOT NULL"]
    params = []

    if geography != "todos":
        where.append("geografia = %s")
        params.append(geography)

    if service1_name != "todos":
        where.append("service1_name = %s")
        params.append(service1_name)

    where_sql = "WHERE " + " AND ".join(where)

    q = f"""
        SELECT 
            TO_CHAR(fecha, 'YYYY-MM') AS month,
            TO_CHAR(fecha, 'Mon YYYY') AS month_label,
            AVG({metric}) AS avg_adoption
        FROM {view}
        {where_sql}
        GROUP BY month, month_label
        ORDER BY month DESC
        LIMIT 12;
    """

    conn = get_db(maturity_level)

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(q, params)
            data = reversed(cur.fetchall())
            return [dict(r) for r in data]

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 14. SERVICE OWNER – KPIs (Radar)
# ============================================================
def get_service_kpis(maturity_level='practitioner',
                     geography='todos',
                     service1_name='todos',
                     date=None):

    if geography == "todos" or service1_name == "todos":
        return None

    view = _get_view_for_level(maturity_level)

    if maturity_level == 'practitioner':
        cols = [
            'rfo_ok_pct', 'dep_pct', 'adopcion_sn2_pct',
            'calidad_features_pct', 'seguridad_pct'
        ]
    else:
        cols = [
            'analisis_review_7dias_pct', 'historias_fix_version_pct', 'repos_nomenclatura_pct',
            'aprobacion_pr_pct', 'tamano_pr_pct', 'repos_chimera_pct', 'tiempo_integracion_pct',
            'tiempo_construcciones_pct', 'construcciones_correctas_pct',
            'tiempo_arreglar_construcciones_pct', 'calidad_codigo_pct',
            'items_pruebas_xray_pct'
        ]

    select_list = [f"COALESCE(AVG({c}), 0) AS {c}" for c in cols]

    month_label_sql = """
        CASE EXTRACT(MONTH FROM MAX(fecha))
            WHEN 1 THEN 'Enero' WHEN 2 THEN 'Febrero' WHEN 3 THEN 'Marzo'
            WHEN 4 THEN 'Abril' WHEN 5 THEN 'Mayo' WHEN 6 THEN 'Junio'
            WHEN 7 THEN 'Julio' WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Septiembre'
            WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre'
        END || ' ' || EXTRACT(YEAR FROM MAX(fecha))
    """

    select_list.append(f"({month_label_sql}) AS month_label")

    where = ["service1_name = %s", "geografia = %s"]
    params = [service1_name, geography]

    if date:
        where.append("TO_CHAR(fecha, 'YYYY-MM') = %s")
        params.append(date)

    where_sql = "WHERE " + " AND ".join(where)

    limit_sql = "" if date else "ORDER BY DATE_TRUNC('month', fecha) DESC LIMIT 1"

    q = f"""
        SELECT {", ".join(select_list)}
        FROM {view}
        {where_sql}
        GROUP BY DATE_TRUNC('month', fecha)
        {limit_sql};
    """

    conn = get_db(maturity_level)

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(q, params)
            r = cur.fetchone()
            if r and r['month_label']:
                return dict(r)
            return None

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# ============================================================
# 15. SERVICE OWNER – Fechas disponibles KPIs
# ============================================================
def get_available_kpi_dates(maturity_level='practitioner',
                            geography='todos',
                            service1_name='todos'):

    if geography == "todos" or service1_name == "todos":
        return []

    view = _get_view_for_level(maturity_level)

    q = f"""
        SELECT DISTINCT
            TO_CHAR(fecha, 'YYYY-MM') AS month,
            TO_CHAR(fecha, 'Mon YYYY') AS month_label
        FROM {view}
        WHERE service1_name = %s AND geografia = %s
        ORDER BY month DESC;
    """

    conn = get_db(maturity_level)

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(q, [service1_name, geography])
            return [dict(r) for r in cur.fetchall()]

    except Exception as e:
        return {"error": str(e)}