# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType
import re

# =========================
# 1️⃣ Rutas ADLS
# =========================
input_path = "abfss://bronze@stbbvadatalake.dfs.core.windows.net/data_sucia/data_sucia_practitioner"
temp_path  = "abfss://silver@stbbvadatalake.dfs.core.windows.net/data_limpia/tmp_practitioner"
final_dir  = "abfss://silver@stbbvadatalake.dfs.core.windows.net/data_limpia/data_limpia_practitioner"
final_file = f"{final_dir}/data_limpia_practitioner.csv"

# =========================
# 2️⃣ Leer CSV desde Bronze
# =========================
df = spark.read.option("header", True).csv(input_path)

# =========================
# 3️⃣ Eliminar columnas no deseadas
# =========================
cols_a_eliminar = [
    "Vulnerab. de alto riesgo por cada mil líneas de códgio",
    "Vulnerab. de alto riesgo por cada mil líneas de códgio mes anterior",
    "Variación de la evolución de vulnerabilidades",
    "Nº de vulnerabilidades high en el mes anterior",
    "Líneas de código en el mes anterior"
]
df = df.drop(*[c for c in cols_a_eliminar if c in df.columns])

# =========================
# 4️⃣ Renombrar columnas finales
# =========================
cols_finales = {
    "period_month": "mes",
    "ug_name": "geografia",
    "uol1_name": "uol1_name",
    "uol2_name": "uol2_name",
    "servicel1_id": "service1_id", 
    "servicel1_name": "service1_name",
    "Nº fichas RFO": "nro_fichas_rfo",
    "Nº SN2 con ficha RFO con status OK": "nro_fichas_rfo_ok",
    "Nº SN2 con dependencias Consumer": "nro_sn2_sn1_dependencias",
    "Nº SN2 del tipo Aplicación no Hijo": "nro_sn2_sn1",
    "Número de features deployed válidas": "nro_features_desplegadas_calidad",
    "Número de features deployed": "nro_features_desplegadas",
    "Valor de cumplimiento de objetivos en Op Model": "puntaje_total_adopcion_sn2",
    "Servicios N2 con medición en el modelo objetivo del Op Model": "sn2_sn1_medidos",
    "Nº de vulnerabilidades high": "total_vulnerabilidades_high",
    "Nº de Lineas de código": "total_lineas_codigo"
}
for old, new in cols_finales.items():
    if old in df.columns:
        df = df.withColumnRenamed(old, new)

# =========================
# 5️⃣ Transformación del mes
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
    import re
    match = re.match(r"(\d{1,2})-([a-z]{3})", valor)
    if match:
        dia, mes_str = match.groups()
        mes_num = meses.get(mes_str[:3], "01")
        return f"{mes_num}/25/2025"
    match = re.match(r"([a-zñ]+)-(\d{2})", valor)
    if match:
        mes_str, anio = match.groups()
        mes_num = meses.get(mes_str[:3], "01")
        return f"{mes_num}/25/20{anio}"
    return valor

spark.udf.register("transformar_mes", transformar_mes)
df = df.withColumn("mes", F.expr("transformar_mes(mes)"))

# =========================
# 6️⃣ Limpiar enteros
# =========================
cols_enteros = [
    "nro_fichas_rfo","nro_fichas_rfo_ok","nro_sn2_sn1_dependencias","nro_sn2_sn1",
    "nro_features_desplegadas_calidad","nro_features_desplegadas",
    "sn2_sn1_medidos","total_vulnerabilidades_high","total_lineas_codigo"
]

for col in cols_enteros:
    if col in df.columns:
        df = df.withColumn(col, F.regexp_replace(col, r"\.", "").cast(DoubleType()))

# =========================
# 7️⃣ Ordenar
# =========================
df = df.orderBy("mes", "geografia", "uol1_name", "uol2_name", "service1_id")

# =========================
# 8️⃣ Guardar TEMPORAL (Spark crea muchos archivos)
# =========================
df.coalesce(1).write.mode("overwrite").option("header", True).csv(temp_path)

# =========================
# 9️⃣ Encontrar el archivo part-*.csv y renombrarlo
# =========================
files = dbutils.fs.ls(temp_path)
csv_temp = [f.path for f in files if f.name.endswith(".csv")][0]

# 10️⃣ Mover a ruta final
dbutils.fs.rm(final_dir, recurse=True)
dbutils.fs.mkdirs(final_dir)
dbutils.fs.mv(csv_temp, final_file)

# 11️⃣ Borrar temporal
dbutils.fs.rm(temp_path, recurse=True)

print("✔️ Limpieza completa y archivo final creado:", final_file)