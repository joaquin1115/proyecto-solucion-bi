-- ============================================================
-- DIMENSION TIEMPO
-- ============================================================
CREATE TABLE dim_tiempo (
    tiempo_id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    dia INT,
    mes INT,
    anio INT
);

-- ============================================================
-- DIMENSION GEOGRAFIA
-- ============================================================
CREATE TABLE dim_geografia (
    geografia_id SERIAL PRIMARY KEY,
    nombre_geografia VARCHAR(200) NOT NULL
);

-- ============================================================
-- DIMENSION SERVICIO N1
-- ============================================================
CREATE TABLE dim_servicio_n1 (
    servicio_n1_id INT PRIMARY KEY,
    nombre_servicio VARCHAR(200),
    nombre_uol1 VARCHAR(200),
    nombre_uol2 VARCHAR(200)
);

-- ============================================================
-- FACT CI
-- ============================================================
CREATE TABLE fact_mediciones_ci (
    fact_id SERIAL PRIMARY KEY,

    tiempo_id INT NOT NULL,
    geografia_id INT NOT NULL,
    servicio_n1_id INT NOT NULL,

    issues_analysis_in_review_menor_7_dias INT,
    issues_analysis_in_review INT,
    historias_deployed_fix_version INT,
    nro_historias_deployed INT,
    repositorios_activos_nomenclatura_estandar INT,
    total_repositorios_activos INT,
    tiempo_medio_aprobacion_pr FLOAT,
    tamano_medio_pr FLOAT,
    repositorios_activos_gobernados_chimera INT,
    tiempo_medio_integracion FLOAT,
    tiempo_medio_construcciones FLOAT,
    ejecuciones_exitosas_pipelines INT,
    ejecuciones_totales_pipelines INT,
    tiempo_medio_reparacion_builds FLOAT,
    repositorios_activos_sonarqube_ok INT,
    repositorios_conectados_sonarqube INT,
    items_pruebas_desplegados_xray INT,
    items_desplegados_totales INT,

    FOREIGN KEY (tiempo_id) REFERENCES dim_tiempo(tiempo_id),
    FOREIGN KEY (geografia_id) REFERENCES dim_geografia(geografia_id),
    FOREIGN KEY (servicio_n1_id) REFERENCES dim_servicio_n1(servicio_n1_id)
);
