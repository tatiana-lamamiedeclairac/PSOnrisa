-- ranking de precios por forma farmaceutica
-- Seleccionamos la base de datos
USE medicamentos_psoriasis;

-- Eliminamos la tabla anterior si ya existe
DROP TABLE IF EXISTS tabla_ranking;

-- Creamos una nueva tabla para guardar el ranking de precios
CREATE TABLE tabla_ranking AS

-- Seleccionamos las columnas necesarias
SELECT
    nregistro, -- Identificador del medicamento para hacer el JOIN después

    nombre, -- Nombre del medicamento

    forma_farmaceutica_simplificada, -- Forma farmacéutica del medicamento

    `Precio de venta al público con IVA` AS pvp_iva, -- Precio de venta

    -- Asignamos un número a cada medicamento según su precio
    ROW_NUMBER() OVER (

        -- Separamos los medicamentos según su forma farmacéutica
        PARTITION BY forma_farmaceutica_simplificada

        -- Ordenamos los precios de mayor a menor
        -- Si dos precios son iguales, utilizamos nregistro para desempatar
        ORDER BY `Precio de venta al público con IVA` DESC, nregistro

    ) AS ranking_precio -- Posición del medicamento dentro de su categoría

-- Obtenemos los datos de la tabla original
FROM medicamentos;


-- Mostramos todos los resultados ordenados por forma y posición
SELECT *
FROM tabla_ranking
ORDER BY forma_farmaceutica_simplificada, ranking_precio;