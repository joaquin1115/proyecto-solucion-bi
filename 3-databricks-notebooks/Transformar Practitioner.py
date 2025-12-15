# Databricks notebook source
# ============================================================
# NOTEBOOK PRACTITIONER → POSTGRESQL (Azure)
# ============================================================

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType

# ============================================================
# 1️⃣ RUTAS EN SILVER (ADLS)
# ============================================================
dbutils.widgets.text("adls_endpoint", "", "1. Endpoint del Data Lake (ej: stxxx.dfs.core.windows.net)")
adls_endpoint = dbutils.widgets.get("adls_endpoint")
dbutils.widgets.text("pg_host", "", "2. Host del servidor PostgreSQL")

input_path  = f"abfss://silver@{adls_endpoint}/data_limpia/data_limpia_practitioner/data_limpia_practitioner.csv"

# ============================================================
# 2️⃣ LEER CSV DESDE SILVER
# ============================================================
df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(input_path)
)

# ============================================================
# 3️⃣ DIMENSION TIEMPO
# ============================================================
dim_tiempo = (
    df.select(F.col("mes").alias("fecha"))
      .distinct()
      .withColumn("dia",  F.dayofmonth("fecha"))
      .withColumn("mes",  F.month("fecha"))       # ✔ coincide con la tabla real
      .withColumn("anio", F.year("fecha"))
      .orderBy("fecha")                           # ✔ del más antiguo al más nuevo
)

# ============================================================
# 4️⃣ DIMENSION GEOGRAFIA
# ============================================================
dim_geografia = (
    df.select("geografia")
      .distinct()
      .withColumnRenamed("geografia", "nombre_geografia")
)

# ============================================================
# 5️⃣ DIMENSION SERVICIO N1
# ============================================================
dim_servicio_n1 = (
    df.select(
        F.col("service1_id").cast("string").alias("servicio_n1_id"),
        F.col("service1_name").alias("nombre_servicio"),     # ✔ corregido
        F.col("uol1_name").alias("nombre_uol1"),             # ✔ corregido
        F.col("uol2_name").alias("nombre_uol2")              # ✔ corregido
    )
    .dropDuplicates(["servicio_n1_id"])
)

# ============================================================
# 6️⃣ CONFIG POSTGRESQL (Azure Flexible Server)
# ============================================================
pg_host = dbutils.widgets.get("pg_host")
jdbc_url = f"jdbc:postgresql://{pg_host}:5432/data_oro_practitioner"

properties = {
    "user": "adminuser",
    "password": "SecurePass123!",     # ✔ tu password real
    "driver": "org.postgresql.Driver",
    "sslmode": "require"
}

# ============================================================
# 7️⃣ LIMPIAR TABLAS (TRUNCATE)
# ============================================================
import psycopg2

conn = psycopg2.connect(
    host=pg_host,
    database="data_oro_practitioner",
    user="adminuser",
    password="SecurePass123!",
    sslmode="require"
)

cur = conn.cursor()

cur.execute("TRUNCATE TABLE fact_mediciones_practitioner RESTART IDENTITY CASCADE;")
cur.execute("TRUNCATE TABLE dim_tiempo RESTART IDENTITY CASCADE;")
cur.execute("TRUNCATE TABLE dim_geografia RESTART IDENTITY CASCADE;")
cur.execute("TRUNCATE TABLE dim_servicio_n1 RESTART IDENTITY CASCADE;")

conn.commit()
cur.close()
conn.close()

# ============================================================
# 8️⃣ INSERTAR DIMENSIONES EN POSTGRESQL
# ============================================================
dim_tiempo.write.jdbc(jdbc_url, "dim_tiempo", mode="append", properties=properties)
dim_geografia.write.jdbc(jdbc_url, "dim_geografia", mode="append", properties=properties)
dim_servicio_n1.write.jdbc(jdbc_url, "dim_servicio_n1", mode="append", properties=properties)

# ============================================================
# 9️⃣ LEER DIMENSIONES DESDE POSTGRES CON ID ASIGNADOS
# ============================================================
dim_tiempo_psql = spark.read.jdbc(jdbc_url, "dim_tiempo", properties=properties)
dim_geografia_psql = spark.read.jdbc(jdbc_url, "dim_geografia", properties=properties)
dim_servicio_n1_psql = spark.read.jdbc(jdbc_url, "dim_servicio_n1", properties=properties)

# ============================================================
# 🔟 PREPARAR DF NORMALIZADO PARA JOIN
# ============================================================
df_norm = df.withColumn("fecha", F.col("mes"))

df_norm = df_norm.withColumn(
    "geografia_norm",
    F.upper(F.trim(F.col("geografia")))
)

df_norm = df_norm.withColumn(
    "service1_id_str",
    F.col("service1_id").cast("string")
)

dim_g_alias = dim_geografia_psql.withColumn(
    "geografia_norm",
    F.upper(F.trim(F.col("nombre_geografia")))
)

dim_s_alias = dim_servicio_n1_psql.withColumn(
    "servicio_n1_id_str",
    F.col("servicio_n1_id").cast("string")
)

# ============================================================
# 1️⃣1️⃣ CREAR TABLA DE HECHOS
# ============================================================
fact = (
    df_norm
    .join(dim_tiempo_psql, df_norm["fecha"] == dim_tiempo_psql["fecha"], "inner")
    .join(dim_g_alias, df_norm["geografia_norm"] == dim_g_alias["geografia_norm"], "inner")
    .join(dim_s_alias, df_norm["service1_id_str"] == dim_s_alias["servicio_n1_id_str"], "inner")
    .select(
        dim_tiempo_psql["tiempo_id"],
        dim_g_alias["geografia_id"],
        dim_s_alias["servicio_n1_id"],
        df_norm["nro_fichas_rfo"],
        df_norm["nro_fichas_rfo_ok"],
        df_norm["nro_sn2_sn1_dependencias"],
        df_norm["nro_sn2_sn1"],
        df_norm["nro_features_desplegadas_calidad"],
        df_norm["nro_features_desplegadas"],
        df_norm["puntaje_total_adopcion_sn2"],
        df_norm["sn2_sn1_medidos"],
        df_norm["total_vulnerabilidades_high"],
        df_norm["total_lineas_codigo"]
    )
)

# ============================================================
# 1️⃣2️⃣ INSERTAR HECHOS EN POSTGRESQL
# ============================================================
fact.write.jdbc(jdbc_url, "fact_mediciones_practitioner", mode="append", properties=properties)