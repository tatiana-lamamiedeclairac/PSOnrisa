-- Seleccionamos la base de datos
USE medicamentos_psoriasis;

-- Eliminamos la tabla anterior si ya existe para poder volver a crearla
DROP TABLE IF EXISTS tabla_densidad;

-- Creamos una nueva tabla para guardar el segundo KPI
CREATE TABLE tabla_densidad AS

-- Seleccionamos las columnas que necesitamos
SELECT
    nregistro, -- Identificador del medicamento para hacer el JOIN después

    nombre, -- Nombre del medicamento

    -- Dividimos el número de palabras de la sección 4.4
    -- entre el número de tablas del documento
    -- NULLIF evita dividir entre cero
    palabras_seccion_4_4 / NULLIF(numero_tablas, 0) AS densidad_ficha

-- Obtenemos los datos de la tabla original
FROM medicamentos;


-- Mostramos la tabla completa para comprobar los resultados
SELECT *
FROM tabla_densidad;