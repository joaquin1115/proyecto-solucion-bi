# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import psycopg2

# =========================================================
# 🔗 Conexión a PostgreSQL (AZURE)
# =========================================================
pg_url = "jdbc:postgresql://pg-bbva-dashboard.postgres.database.azure.com:5432/data_oro_ci?sslmode=require"

pg_properties = {
    "user": "adminuser",
    "password": "SecurePass123!",
    "driver": "org.postgresql.Driver"
}

# =========================================================
# 1️⃣ Leer tabla de hechos + dimensiones
# =========================================================
fact_mediciones_ci = spark.read.jdbc(pg_url, "fact_mediciones_ci", properties=pg_properties)
dim_tiempo = spark.read.jdbc(pg_url, "dim_tiempo", properties=pg_properties)
dim_geografia = spark.read.jdbc(pg_url, "dim_geografia", properties=pg_properties)
dim_servicio_n1 = spark.read.jdbc(pg_url, "dim_servicio_n1", properties=pg_properties)

# =========================================================
# 2️⃣ Star Join
# =========================================================
df = (
    fact_mediciones_ci.alias("fm")
    .join(dim_tiempo.alias("dt"), F.col("fm.tiempo_id") == F.col("dt.tiempo_id"))
    .join(dim_geografia.alias("dg"), F.col("fm.geografia_id") == F.col("dg.geografia_id"))
    .join(dim_servicio_n1.alias("dsn1"), F.col("fm.servicio_n1_id") == F.col("dsn1.servicio_n1_id"))
    .select(
        F.col("dt.fecha"),
        F.col("dt.mes"),
        F.col("dt.anio"),
        F.col("dg.nombre_geografia").alias("geografia"),
        F.col("dsn1.nombre_servicio").alias("service1_name"),

        # Métricas originales (fact)
        "issues_analysis_in_review_menor_7_dias",
        "issues_analysis_in_review",
        "historias_deployed_fix_version",
        "nro_historias_deployed",
        "repositorios_activos_nomenclatura_estandar",
        "total_repositorios_activos",
        "tiempo_medio_aprobacion_pr",
        "tamano_medio_pr",
        "repositorios_activos_gobernados_chimera",
        "tiempo_medio_integracion",
        "tiempo_medio_construcciones",
        "ejecuciones_exitosas_pipelines",
        "ejecuciones_totales_pipelines",
        "tiempo_medio_reparacion_builds",
        "repositorios_activos_sonarqube_ok",
        "repositorios_conectados_sonarqube",
        "items_pruebas_desplegados_xray",
        "items_desplegados_totales"
    )
)

# =========================================================
# 3️⃣ Calcular los 13 KPI de CI
# =========================================================

df_calc = (
    df
    .withColumn("analisis_review_7dias_pct",
        F.when(F.col("issues_analysis_in_review") > 0,
               F.round(F.col("issues_analysis_in_review_menor_7_dias") /
                       F.col("issues_analysis_in_review") * 100, 2))
    )
    .withColumn("historias_fix_version_pct",
        F.when(F.col("nro_historias_deployed") > 0,
               F.round(F.col("historias_deployed_fix_version") /
                       F.col("nro_historias_deployed") * 100, 2))
    )
    .withColumn("repos_nomenclatura_pct",
        F.when(F.col("total_repositorios_activos") > 0,
               F.round(F.col("repositorios_activos_nomenclatura_estandar") /
                       F.col("total_repositorios_activos") * 100, 2))
    )
    .withColumn("aprobacion_pr_pct",
        F.when(F.col("tiempo_medio_aprobacion_pr") < 1, F.lit(90))
         .when(F.col("tiempo_medio_aprobacion_pr") < 1.5, F.lit(70))
         .when(F.col("tiempo_medio_aprobacion_pr") < 3, F.lit(30))
         .otherwise(F.lit(0))
    )
    .withColumn("tamano_pr_pct",
        F.when(F.col("tamano_medio_pr") < 300, F.lit(90))
         .when(F.col("tamano_medio_pr") < 400, F.lit(70))
         .when(F.col("tamano_medio_pr") < 600, F.lit(30))
         .otherwise(F.lit(0))
    )
    .withColumn("repos_chimera_pct",
        F.when(F.col("total_repositorios_activos") > 0,
               F.round(F.col("repositorios_activos_gobernados_chimera") /
                       F.col("total_repositorios_activos") * 100, 2))
    )
    .withColumn("tiempo_integracion_pct",
        F.when(F.col("tiempo_medio_integracion") < 3, F.lit(90))
         .when(F.col("tiempo_medio_integracion") < 4, F.lit(70))
         .when(F.col("tiempo_medio_integracion") < 6, F.lit(30))
         .otherwise(F.lit(0))
    )
    .withColumn("tiempo_construcciones_pct",
        F.when(F.col("tiempo_medio_construcciones") < 20, F.lit(90))
         .when(F.col("tiempo_medio_construcciones") < 35, F.lit(70))
         .when(F.col("tiempo_medio_construcciones") < 45, F.lit(30))
         .otherwise(F.lit(0))
    )
    .withColumn("construcciones_correctas_pct",
        F.when(F.col("ejecuciones_totales_pipelines") > 0,
               F.round(F.col("ejecuciones_exitosas_pipelines") /
                       F.col("ejecuciones_totales_pipelines") * 100, 2))
    )
    .withColumn("tiempo_arreglar_construcciones_pct",
        F.when(F.col("tiempo_medio_reparacion_builds") < 60, F.lit(90))
         .when(F.col("tiempo_medio_reparacion_builds") < 120, F.lit(70))
         .when(F.col("tiempo_medio_reparacion_builds") < 180, F.lit(30))
         .otherwise(F.lit(0))
    )
    .withColumn("calidad_codigo_pct",
        F.when(F.col("repositorios_conectados_sonarqube") > 0,
               F.round(F.col("repositorios_activos_sonarqube_ok") /
                       F.col("repositorios_conectados_sonarqube") * 100, 2))
    )
    .withColumn("items_pruebas_xray_pct",
        F.when(F.col("items_desplegados_totales") > 0,
               F.round(F.col("items_pruebas_desplegados_xray") /
                       F.col("items_desplegados_totales") * 100, 2))
    )
)

# =========================================================
# 4️⃣ Adopción total ponderada (igual que Practitioner)
# =========================================================
pesos_ci = {
    "analisis_review_7dias_pct": 5,
    "historias_fix_version_pct": 6,
    "repos_nomenclatura_pct": 6,
    "aprobacion_pr_pct": 10,
    "tamano_pr_pct": 5,
    "repos_chimera_pct": 7,
    "tiempo_integracion_pct": 16,
    "tiempo_construcciones_pct": 9,
    "construcciones_correctas_pct": 13,
    "tiempo_arreglar_construcciones_pct": 8,
    "calidad_codigo_pct": 10,
    "items_pruebas_xray_pct": 5
}

df_calc = df_calc.withColumn(
    "suma_pesada",
    sum(
        F.when(F.col(k).isNotNull(), F.col(k) * v)
         .otherwise(F.lit(0))
        for k, v in pesos_ci.items()
    )
).withColumn(
    "suma_pesos",
    sum(
        F.when(F.col(k).isNotNull(), F.lit(v))
         .otherwise(F.lit(0))
        for k, v in pesos_ci.items()
    )
).withColumn(
    "adopcion_total_pct",
    F.when(F.col("suma_pesos") > 0,
           F.round(F.col("suma_pesada") / F.col("suma_pesos"), 2))
     .otherwise(F.lit(None).cast("double"))
)

# =========================================================
# 5️⃣ Selección final
# =========================================================
fact_final_ci = df_calc.select(
    "fecha",
    "geografia",
    "service1_name",
    "analisis_review_7dias_pct",
    "historias_fix_version_pct",
    "repos_nomenclatura_pct",
    "aprobacion_pr_pct",
    "tamano_pr_pct",
    "repos_chimera_pct",
    "tiempo_integracion_pct",
    "tiempo_construcciones_pct",
    "construcciones_correctas_pct",
    "tiempo_arreglar_construcciones_pct",
    "calidad_codigo_pct",
    "items_pruebas_xray_pct",
    "adopcion_total_pct"
)

# =========================================================
# 6️⃣ Crear la VISTA normal en PostgreSQL (MISMO PATRÓN QUE PRACTITIONER)
# =========================================================
def execute_postgres(query):
    conn = psycopg2.connect(
        host="pg-bbva-dashboard.postgres.database.azure.com",
        port=5432,
        database="data_oro_ci",
        user="adminuser",
        password="SecurePass123!",
        sslmode="require"
    )
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

# 1️⃣ Borrar vista si existe
execute_postgres("DROP VIEW IF EXISTS vw_ci_kpis;")

# 2️⃣ Crear tabla FINAL (NO temporal)
fact_final_ci.write.jdbc(
    url=pg_url,
    table="table_ci_kpis",   # <-- Igual que Practitioner (table_practitioner_kpis)
    mode="overwrite",
    properties=pg_properties
)

# 3️⃣ Crear vista que apunta a la tabla
execute_postgres("""
    CREATE VIEW vw_ci_kpis AS
    SELECT * FROM table_ci_kpis;
""")

print("✔ Vista creada correctamente: vw_ci_kpis")