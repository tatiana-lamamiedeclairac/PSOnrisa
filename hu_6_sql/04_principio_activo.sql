-- Cálculo del precio por principio activo de cada medicamento
-- Seleccionamos la base de datos
USE medicamentos_psoriasis;

-- Eliminamos la tabla anterior si ya existe para poder volver a crearla
DROP TABLE IF EXISTS tabla_precio_activo;

-- Creamos una nueva tabla para guardar el cuarto KPI
CREATE TABLE tabla_precio_activo AS

-- Seleccionamos las columnas que necesitamos
SELECT
    nregistro, -- Identificador del medicamento para hacer el JOIN después

    nombre, -- Nombre del medicamento

    -- Dividimos el precio de venta entre el número de principios activos
    -- NULLIF evita dividir entre cero
    `Precio de venta al público con IVA`
    / NULLIF(num_principios_activos, 0) AS precio_por_principio_activo

-- Obtenemos los datos de la tabla original
FROM medicamentos;


-- Mostramos la tabla completa para comprobar los resultados
SELECT *
FROM tabla_precio_activo;