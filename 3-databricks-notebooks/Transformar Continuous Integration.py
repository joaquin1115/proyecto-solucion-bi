# Databricks notebook source
from pyspark.sql import functions as F
import psycopg2

# ==========================================
# 1️⃣ Leer CSV desde ADLS (Silver)
# ==========================================
dbutils.widgets.text("adls_endpoint", "", "1. Endpoint del Data Lake (ej: stxxx.dfs.core.windows.net)")
adls_endpoint = dbutils.widgets.get("adls_endpoint")

path_ci = f"abfss://silver@{adls_endpoint}/data_limpia/data_limpia_continuous_integration/data_limpia_continuous_integration.csv"

df = spark.read.csv(path_ci, header=True, inferSchema=True)
df = df.withColumn("fecha", F.to_date(F.col("mes"), "MM/dd/yyyy"))

# ==========================================
# 2️⃣ CREAR DIMENSIONES -------------------------------------------------------
# ==========================================

# -------- DIM TIEMPO (ordenada por mes ascendente)
dim_tiempo = (
    df.select("fecha")
      .distinct()
      .withColumn("dia", F.dayofmonth("fecha"))
      .withColumn("mes", F.month("fecha"))
      .withColumn("anio", F.year("fecha"))
      .orderBy("anio", "mes")               # ← orden correcto
)

# -------- DIM GEOGRAFIA
dim_geografia = (
    df.select("geografia")
      .distinct()
      .withColumnRenamed("geografia", "nombre_geografia")
)

# -------- DIM SERVICIO N1
dim_servicio_n1 = (
    df.select(
        F.col("service1_id").cast("int").alias("servicio_n1_id"),
        F.col("service1_name").alias("nombre_servicio"),
        F.col("uol1_name").alias("nombre_uol1"),
        F.col("uol2_name").alias("nombre_uol2")
    )
    .dropDuplicates(["servicio_n1_id"])
    .repartition(1)
)

# ==========================================
# 3️⃣ CONFIG PGSQL
# ==========================================
jdbc_url = "jdbc:postgresql://pg-bbva-dashboard.postgres.database.azure.com:5432/data_oro_ci?sslmode=require"
properties = {
    "user": "adminuser",
    "password": "SecurePass123!",
    "driver": "org.postgresql.Driver"
}

# ==========================================
# 4️⃣ TRUNCATE + RESET IDs
# ==========================================
conn = psycopg2.connect(
    host="pg-bbva-dashboard.postgres.database.azure.com",
    database="data_oro_ci",
    user="adminuser",
    password="SecurePass123!",
    sslmode="require"
)
cur = conn.cursor()

cur.execute("TRUNCATE TABLE fact_mediciones_ci RESTART IDENTITY CASCADE;")
cur.execute("TRUNCATE TABLE dim_tiempo RESTART IDENTITY CASCADE;")
cur.execute("TRUNCATE TABLE dim_geografia RESTART IDENTITY CASCADE;")
cur.execute("DELETE FROM dim_servicio_n1;")

# Reset proper identity sequences
cur.execute("ALTER SEQUENCE dim_tiempo_tiempo_id_seq RESTART WITH 1;")
cur.execute("ALTER SEQUENCE dim_geografia_geografia_id_seq RESTART WITH 1;")

conn.commit()
cur.close()
conn.close()

# ==========================================
# 5️⃣ INSERTAR DIMENSIONES
# ==========================================
dim_tiempo.write.jdbc(url=jdbc_url, table="dim_tiempo", mode="append", properties=properties)
dim_geografia.write.jdbc(url=jdbc_url, table="dim_geografia", mode="append", properties=properties)
dim_servicio_n1.write.jdbc(url=jdbc_url, table="dim_servicio_n1", mode="append", properties=properties)

# ==========================================
# 6️⃣ LEER DIMENSIONES INSERTADAS
# ==========================================
dim_tiempo_psql = spark.read.jdbc(url=jdbc_url, table="dim_tiempo", properties=properties)
dim_geografia_psql = spark.read.jdbc(url=jdbc_url, table="dim_geografia", properties=properties)
dim_servicio_n1_psql = spark.read.jdbc(url=jdbc_url, table="dim_servicio_n1", properties=properties)

# ==========================================
# 7️⃣ BUILDEAR FACT CI
# ==========================================
df_norm = df.withColumn("geografia_norm", F.upper(F.trim(F.col("geografia"))))
dim_g_alias = dim_geografia_psql.withColumn("geografia_norm", F.upper(F.trim(F.col("nombre_geografia"))))

fact = (
    df_norm
    .join(dim_tiempo_psql, df_norm["fecha"] == dim_tiempo_psql["fecha"], "inner")
    .join(dim_g_alias, df_norm["geografia_norm"] == dim_g_alias["geografia_norm"], "inner")
    .join(dim_servicio_n1_psql, df_norm["service1_id"].cast("int") == dim_servicio_n1_psql["servicio_n1_id"], "inner")
    .select(
        dim_tiempo_psql["tiempo_id"],
        dim_g_alias["geografia_id"],
        dim_servicio_n1_psql["servicio_n1_id"],
        df_norm["issues_analysis_in_review_menor_7_dias"].cast("int"),
        df_norm["issues_analysis_in_review"].cast("int"),
        df_norm["historias_deployed_fix_version"].cast("int"),
        df_norm["nro_historias_deployed"].cast("int"),
        df_norm["repositorios_activos_nomenclatura_estandar"].cast("int"),
        df_norm["total_repositorios_activos"].cast("int"),
        df_norm["tiempo_medio_aprobacion_pr"].cast("float"),
        df_norm["tamano_medio_pr"].cast("float"),
        df_norm["repositorios_activos_gobernados_chimera"].cast("int"),
        df_norm["tiempo_medio_integracion"].cast("float"),
        df_norm["tiempo_medio_construcciones"].cast("float"),
        df_norm["ejecuciones_exitosas_pipelines"].cast("int"),
        df_norm["ejecuciones_totales_pipelines"].cast("int"),
        df_norm["tiempo_medio_reparacion_builds"].cast("float"),
        df_norm["repositorios_activos_sonarqube_ok"].cast("int"),
        df_norm["repositorios_conectados_sonarqube"].cast("int"),
        df_norm["items_pruebas_desplegados_xray"].cast("int"),
        df_norm["items_desplegados_totales"].cast("int")
    )
)

# ==========================================
# 8️⃣ INSERTAR FACT CI
# ==========================================
fact.write.jdbc(
    url=jdbc_url,
    table="fact_mediciones_ci",
    mode="append",
    properties=properties
)