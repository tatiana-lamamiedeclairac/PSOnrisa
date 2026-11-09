USE medicamentos_psoriasis;

-- Eliminamos la tabla si ya existe
DROP TABLE IF EXISTS tabla_kpi;

-- Creamos una tabla con los cinco KPI
CREATE TABLE tabla_kpi AS

SELECT
    tabla_desviacion.nregistro,
    tabla_desviacion.desviacion_precio,
    tabla_densidad.densidad_ficha,
    tabla_margen.margen_economico,
    tabla_precio_activo.precio_por_principio_activo,
    tabla_ranking.ranking_precio

-- Partimos de la primera tabla de KPI
FROM tabla_desviacion

-- Unimos las demás tablas por el identificador del medicamento
LEFT JOIN tabla_densidad
    ON tabla_desviacion.nregistro = tabla_densidad.nregistro

LEFT JOIN tabla_margen
    ON tabla_desviacion.nregistro = tabla_margen.nregistro

LEFT JOIN tabla_precio_activo
    ON tabla_desviacion.nregistro = tabla_precio_activo.nregistro

LEFT JOIN tabla_ranking
    ON tabla_desviacion.nregistro = tabla_ranking.nregistro;


-- Mostramos la tabla con los cinco KPI
SELECT *
FROM tabla_kpi;