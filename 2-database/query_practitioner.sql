-- ============================================================
-- DIMENSION TIEMPO
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_tiempo (
    tiempo_id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    dia INT,
    mes INT,
    anio INT
);

-- ============================================================
-- DIMENSION GEOGRAFIA
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_geografia (
    geografia_id SERIAL PRIMARY KEY,
    nombre_geografia VARCHAR(200) NOT NULL
);

-- ============================================================
-- DIMENSION SERVICIO N1
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_servicio_n1 (
    servicio_n1_id VARCHAR(50) PRIMARY KEY,
    nombre_servicio VARCHAR(200),
    nombre_uol1 VARCHAR(200),
    nombre_uol2 VARCHAR(200)
);

-- ============================================================
-- TABLA DE HECHOS PRACTITIONER
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_mediciones_practitioner (
    fact_id SERIAL PRIMARY KEY,

    tiempo_id INT NOT NULL,
    geografia_id INT NOT NULL,
    servicio_n1_id VARCHAR(50) NOT NULL,

    nro_fichas_rfo INT,
    nro_fichas_rfo_ok INT,
    nro_sn2_sn1_dependencias INT,
    nro_sn2_sn1 INT,
    nro_features_desplegadas_calidad INT,
    nro_features_desplegadas INT,
    puntaje_total_adopcion_sn2 FLOAT,
    sn2_sn1_medidos INT,
    total_vulnerabilidades_high INT,
    total_lineas_codigo INT,

    FOREIGN KEY (tiempo_id) REFERENCES dim_tiempo(tiempo_id),
    FOREIGN KEY (geografia_id) REFERENCES dim_geografia(geografia_id),
    FOREIGN KEY (servicio_n1_id) REFERENCES dim_servicio_n1(servicio_n1_id)
);