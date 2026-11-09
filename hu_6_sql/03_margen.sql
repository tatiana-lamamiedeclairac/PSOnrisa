-- Seleccionamos la base de datos
USE medicamentos_psoriasis;

-- Eliminamos la tabla anterior si existe para poder volver a crearla
DROP TABLE IF EXISTS tabla_margen;

-- Creamos una nueva tabla para guardar el tercer KPI
CREATE TABLE tabla_margen AS

-- Seleccionamos las columnas que necesitamos
SELECT
    nregistro, -- Identificador del medicamento para hacer el JOIN después

    nombre, -- Nombre del medicamento

    -- Restamos el precio de referencia al precio de venta con IVA
    -- Guardamos el resultado en una columna llamada margen_economico
    (`Precio de venta al público con IVA` - `Precio de referencia`) AS margen_economico

-- Obtenemos los datos de la tabla original
FROM medicamentos;


-- Mostramos la tabla completa para comprobar los resultados
SELECT *
FROM tabla_margen;