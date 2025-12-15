# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, round as spark_round, lag, lit, sum as Fsum,
    concat_ws, to_date, monotonically_increasing_id
)
from pyspark.sql.window import Window
import psycopg2

# ======================================================
# 0️⃣ CONFIG — CONEXIÓN AZURE POSTGRESQL
# ======================================================

dbutils.widgets.text("pg_host", "", "Host del servidor PostgreSQL")
pg_host = dbutils.widgets.get("pg_host")
pg_url = f"jdbc:postgresql://{pg_host}:5432/data_oro_practitioner"
pg_properties = {
    "user": "adminuser",
    "password": "SecurePass123!",
    "driver": "org.postgresql.Driver",
    "sslmode": "require"
}

# ======================================================
# 1️⃣ LEER TABLAS DEL DATAWAREHOUSE (EN POSTGRESQL)
# ======================================================

fact = spark.read.jdbc(pg_url, "fact_mediciones_practitioner", properties=pg_properties)
dim_tiempo = spark.read.jdbc(pg_url, "dim_tiempo", properties=pg_properties)
dim_geografia = spark.read.jdbc(pg_url, "dim_geografia", properties=pg_properties)
dim_servicio = spark.read.jdbc(pg_url, "dim_servicio_n1", properties=pg_properties)

# ======================================================
# 2️⃣ UNIR FACT + DIMENSIONES (MODELO ESTRELLA)
# ======================================================

df = (
    fact.alias("f")
    .join(dim_tiempo.alias("t"), col("f.tiempo_id") == col("t.tiempo_id"))
    .join(dim_geografia.alias("g"), col("f.geografia_id") == col("g.geografia_id"))
    .join(dim_servicio.alias("s"), col("f.servicio_n1_id") == col("s.servicio_n1_id"))
    .select(
        col("t.mes"),
        col("t.anio"),
        col("g.nombre_geografia").alias("geografia"),
        col("s.nombre_servicio").alias("service1_name"),

        col("f.nro_fichas_rfo"),
        col("f.nro_fichas_rfo_ok"),
        col("f.nro_sn2_sn1"),
        col("f.nro_sn2_sn1_dependencias"),
        col("f.sn2_sn1_medidos"),
        col("f.puntaje_total_adopcion_sn2"),
        col("f.nro_features_desplegadas"),
        col("f.nro_features_desplegadas_calidad"),
        col("f.total_vulnerabilidades_high"),
        col("f.total_lineas_codigo")
    )
)

# ======================================================
# 3️⃣ CREAR FECHA COMPLETA YYYY-MM-01
# ======================================================

df = df.withColumn(
    "fecha",
    to_date(concat_ws("-", col("anio"), col("mes"), lit("01")), "yyyy-M-dd")
)

# ======================================================
# 4️⃣ CALCULAR KPIs
# ======================================================

df_calc = (
    df
    .withColumn("rfo_ok_pct",
        when(col("nro_fichas_rfo") > 0,
             spark_round(col("nro_fichas_rfo_ok") / col("nro_fichas_rfo") * 100, 2)
        )
    )
    .withColumn("dep_pct",
        when(col("nro_sn2_sn1") > 0,
             spark_round(col("nro_sn2_sn1_dependencias") / col("nro_sn2_sn1") * 100, 2)
        )
    )
    .withColumn("adopcion_sn2_pct",
        when(col("sn2_sn1_medidos") > 0,
             spark_round(col("puntaje_total_adopcion_sn2") / col("sn2_sn1_medidos") * 100, 2)
        )
    )
    .withColumn("calidad_features_pct",
        when(col("nro_features_desplegadas") > 0,
             spark_round(col("nro_features_desplegadas_calidad") / col("nro_features_desplegadas") * 100, 2)
        )
    )
    .withColumn("vuln_actual",
        when(col("total_lineas_codigo") > 0,
             col("total_vulnerabilidades_high") / col("total_lineas_codigo") * 1000
        )
    )
)

# ======================================================
# 5️⃣ NECESITA MES ANTERIOR
# ======================================================

df_calc = df_calc.withColumn(
    "necesita_mes_anterior",
    when((col("total_lineas_codigo") <= 0)
         | (col("vuln_actual") < 0.04)
         | (col("vuln_actual") > 0.2),
         False
    ).otherwise(True)
)

# ======================================================
# 6️⃣ CALCULO CON MES ANTERIOR
# ======================================================

window_prev = Window.partitionBy("geografia", "service1_name").orderBy("fecha")

df_calc = (
    df_calc
    .withColumn("total_vulnerabilidades_high_prev",
        when(col("necesita_mes_anterior"),
             lag("total_vulnerabilidades_high").over(window_prev)
        )
    )
    .withColumn("total_lineas_codigo_prev",
        when(col("necesita_mes_anterior"),
             lag("total_lineas_codigo").over(window_prev)
        )
    )
    .withColumn("vuln_anterior",
        when(~col("necesita_mes_anterior"), None)
        .when(col("total_lineas_codigo_prev").isNull(), lit(-99))
        .when(col("total_lineas_codigo_prev") <= 0, lit(-99))
        .otherwise(col("total_vulnerabilidades_high_prev") / col("total_lineas_codigo_prev") * 1000)
    )
    .withColumn("evol_vuln",
        when(~col("necesita_mes_anterior"), None)
        .when(col("vuln_anterior") == -99, None)
        .when(col("vuln_anterior") == 0, None)
        .otherwise((col("vuln_actual") - col("vuln_anterior")) / col("vuln_anterior") * 100)
    )
)

# ======================================================
# 7️⃣ KPI SEGURIDAD
# ======================================================

df_calc = df_calc.withColumn(
    "seguridad_pct",
    when(col("total_lineas_codigo") <= 0, None)
    .when(col("vuln_actual") < 0.04, lit(100))
    .when(col("vuln_actual") > 0.2, lit(0))
    .when(col("vuln_anterior") == -99, None)
    .when(col("evol_vuln").isNull(), None)
    .when(col("evol_vuln") == -100, lit(0))
    .when(col("evol_vuln") <= -10, lit(100))
    .when((col("evol_vuln") > -10) & (col("evol_vuln") < 0), lit(75))
    .when(col("evol_vuln") == 0, lit(50))
    .when((col("evol_vuln") > 0) & (col("evol_vuln") < 10), lit(25))
    .when(col("evol_vuln") >= 10, lit(0))
)

# ======================================================
# 8️⃣ ADOPCIÓN TOTAL (PONDERADA)
# ======================================================

pesos = {
    "rfo_ok_pct": 13,
    "dep_pct": 13,
    "adopcion_sn2_pct": 27,
    "calidad_features_pct": 20,
    "seguridad_pct": 27
}

df_calc = df_calc.withColumn(
    "suma_pesada",
    sum(when(col(k).isNotNull(), col(k) * v).otherwise(0) for k, v in pesos.items())
).withColumn(
    "suma_pesos",
    sum(when(col(k).isNotNull(), lit(v)).otherwise(0) for k, v in pesos.items())
).withColumn(
    "adopcion_total_pct",
    when(col("suma_pesos") > 0,
         spark_round(col("suma_pesada") / col("suma_pesos"), 2)
    ).otherwise(None)
)

# ======================================================
# 9️⃣ TABLA FINAL PARA LA VISTA
# ======================================================

vista_df = df_calc.select(
    "fecha",
    "geografia",
    "service1_name",
    "rfo_ok_pct",
    "dep_pct",
    "adopcion_sn2_pct",
    "calidad_features_pct",
    "seguridad_pct",
    "adopcion_total_pct"
)

# ======================================================
# 🔟 CREAR / REEMPLAZAR VISTA NORMAL
# ======================================================

def run_pg(query):
    conn = psycopg2.connect(
        host=pg_host,
        port=5432,
        database="data_oro_practitioner",
        user="adminuser",
        password="SecurePass123!",
        sslmode="require"
    )
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

# Borrar vista sin afectar tabla
run_pg("DROP VIEW IF EXISTS vw_practitioner_kpis;")

# Crear tabla base y luego vista
vista_df.write.jdbc(
    url=pg_url,
    table="table_practitioner_kpis",
    mode="overwrite",
    properties=pg_properties
)

run_pg("""
    CREATE VIEW vw_practitioner_kpis AS
    SELECT * FROM table_practitioner_kpis;
""")

print("✔ Vista creada correctamente: vw_practitioner_kpis")