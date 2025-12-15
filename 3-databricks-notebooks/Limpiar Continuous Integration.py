# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType
import re, time

# =========================
# 1️⃣ RUTAS ADLS CORRECTAS
# =========================
input_path = "abfss://bronze@stbbvadatalake.dfs.core.windows.net/data_sucia/data_sucia_continuous_integration"
temp_path  = "abfss://silver@stbbvadatalake.dfs.core.windows.net/tmp_continuous_integration"
final_dir  = "abfss://silver@stbbvadatalake.dfs.core.windows.net/data_limpia/data_limpia_continuous_integration"
final_file = f"{final_dir}/data_limpia_continuous_integration.csv"

# =========================
# 2️⃣ LEER CSV DESDE ADLS
# =========================
df = spark.read.option("header", True).option("delimiter", ",").csv(input_path)

# =========================
# 3️⃣ RENAME COLUMNAS
# =========================
cols_finales = {
    "period_month": "mes",
    "ug_name": "geografia",
    "uol1_name": "uol1_name",
    "uol2_name": "uol2_name",
    "servicel1_id": "service1_id",
    "servicel1_name": "service1_name",
    "issues_review_menor_7_dias": "issues_analysis_in_review_menor_7_dias",
    "issues_en_revision_total": "issues_analysis_in_review",
    "historias_fix_version_deploy": "historias_deployed_fix_version",
    "cantidad_historias_deploy": "nro_historias_deployed",
    "repos_activos_con_nomenclatura_estandar": "repositorios_activos_nomenclatura_estandar",
    "total_repositorios_en_uso": "total_repositorios_activos",
    "promedio_tiempo_aprobacion_pr": "tiempo_medio_aprobacion_pr",
    "promedio_tamano_pr": "tamano_medio_pr",
    "repos_gobernados_chimera_activos": "repositorios_activos_gobernados_chimera",
    "promedio_tiempo_integracion": "tiempo_medio_integracion",
    "promedio_tiempo_builds": "tiempo_medio_construcciones",
    "pipelines_ejecuciones_exitosas": "ejecuciones_exitosas_pipelines",
    "pipelines_ejecuciones_totales": "ejecuciones_totales_pipelines",
    "promedio_tiempo_reparacion_builds": "tiempo_medio_reparacion_builds",
    "repos_sonarqube_ok_activos": "repositorios_activos_sonarqube_ok",
    "repos_conectados_sonarqube": "repositorios_conectados_sonarqube",
    "items_pruebas_desplegados_xray": "items_pruebas_desplegados_xray",
    "items_desplegados_totales": "items_desplegados_totales"
}

for old, new in cols_finales.items():
    if old in df.columns:
        df = df.withColumnRenamed(old, new)

# =========================
# 4️⃣ UDF FECHA
# =========================
def transformar_mes(valor):
    if not valor:
        return valor

    meses = {
        "jan":"01","feb":"02","mar":"03","apr":"04","may":"05","jun":"06",
        "jul":"07","aug":"08","sep":"09","oct":"10","nov":"11","dec":"12",
        "ene":"01","abr":"04","ago":"08","dic":"12"
    }

    valor = valor.strip().lower()

    m1 = re.match(r"(\d{1,2})-([a-zñ]{3})", valor)
    if m1:
        _, mes = m1.groups()
        return f"{meses.get(mes,'01')}/25/2025"

    m2 = re.match(r"([a-zñ]{3})-(\d{2})", valor)
    if m2:
        mes, anio = m2.groups()
        return f"{meses.get(mes,'01')}/25/20{anio}"

    return valor

spark.udf.register("transformar_mes", transformar_mes, StringType())
df = df.withColumn("mes", F.expr("transformar_mes(mes)"))

# =========================
# 5️⃣ LIMPIAR NÚMEROS
# =========================
cols_int = [
 "issues_analysis_in_review_menor_7_dias","issues_analysis_in_review",
 "historias_deployed_fix_version","nro_historias_deployed",
 "repositorios_activos_nomenclatura_estandar","total_repositorios_activos",
 "repositorios_activos_gobernados_chimera",
 "ejecuciones_exitosas_pipelines","ejecuciones_totales_pipelines",
 "repositorios_activos_sonarqube_ok","repositorios_conectados_sonarqube",
 "items_pruebas_desplegados_xray","items_desplegados_totales"
]

for c in cols_int:
    if c in df.columns:
        df = df.withColumn(c, F.regexp_replace(F.col(c), r"\.", "").cast(DoubleType()))

cols_float = [
 "tiempo_medio_aprobacion_pr","tamano_medio_pr",
 "tiempo_medio_integracion","tiempo_medio_construcciones",
 "tiempo_medio_reparacion_builds"
]

for c in cols_float:
    if c in df.columns:
        df = df.withColumn(c, F.col(c).cast(DoubleType()))

# =========================
# 6️⃣ ORDENAR
# =========================
df = df.orderBy("mes","geografia","uol1_name","uol2_name","service1_id")

# =========================
# 7️⃣ GUARDAR EN TEMPORAL
# =========================
df.coalesce(1).write.mode("overwrite").option("header", True).csv(temp_path)

# =========================
# 8️⃣ MOVER CSV FINAL
# =========================
files = dbutils.fs.ls(temp_path)
csv_file = [f.path for f in files if f.path.endswith(".csv")][0]

dbutils.fs.mkdirs(final_dir)
dbutils.fs.rm(final_file, True)
dbutils.fs.mv(csv_file, final_file)

# =========================
# 9️⃣ LIMPIAR TEMP
# =========================
dbutils.fs.rm(temp_path, True)

print("✅ Archivo final generado correctamente en:")
print(final_file)