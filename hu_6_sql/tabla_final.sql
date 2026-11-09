USE medicamentos_psoriasis;

-- Eliminamos la tabla final si ya existe
DROP TABLE IF EXISTS tabla_final;

-- Creamos una tabla con todas las columnas originales y los KPI
CREATE TABLE tabla_final AS

SELECT *
FROM medicamentos

-- Unimos ambas tablas utilizando nregistro
LEFT JOIN tabla_kpi
USING (nregistro);

-- Mostramos la tabla final
SELECT *
FROM tabla_final;