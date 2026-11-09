-- Seleccionamos la base de datos en la que vamos a trabajar
USE medicamentos_psoriasis;

-- Eliminamos la tabla anterior si ya existe para poder volver a crearla
DROP TABLE IF EXISTS tabla_desviacion;

-- Creamos una nueva tabla donde guardaremos el primer KPI
CREATE TABLE tabla_desviacion AS

-- Seleccionamos las columnas que necesitamos de la tabla original
SELECT
    nregistro, -- Identificador de cada medicamento para unir las tablas después

    nombre, -- Nombre del medicamento para poder identificarlo

    -- Restamos el precio de referencia al precio de venta
    -- Dividimos el resultado entre el precio de referencia
    -- Multiplicamos por 100 para obtener el porcentaje
    (`Precio de venta al público con IVA` - `Precio de referencia`)
    / NULLIF(`Precio de referencia`, 0) * 100 AS desviacion_precio

    -- nullif comprueba si el precio de referencia es igual a 0, si lo es devuelve null y si no 
    -- devuelve el precio de referencia 

-- Indicamos de qué tabla obtenemos los datos
FROM medicamentos;


-- Comprobamos que se ha creado correctamente la tabla
SELECT *
FROM tabla_desviacion;

-- aparecen nulls y 0 porque 
-- null: porque no se han recogido el precio para ese medicamento
-- 0: porque como los precios son iguales con iva y sin iva la diferencia es 0. 