
import pandas as pd
import matplotlib.pyplot as plt


def cargar_datos(ruta):
    # Leemos el Excel original
    return pd.read_excel(ruta)



def explorar_datos(df):
    # Definimos una función que recibe un DataFrame llamado df

    # Muestra el número de filas, columnas, tipos de datos y valores no nulos
    df.info()

    # Muestra estadísticas de las columnas numéricas:
    # cantidad, media, desviación típica, mínimo, cuartiles y máximo
    print(df.describe())

    # Imprime un título y \n añade un salto de línea
    print("\nValores nulos:")

    # isna() comprueba qué valores son nulos (True o False)
    # sum() cuenta los True, obteniendo los nulos de cada columna
    print(df.isna().sum())

    # duplicated() detecta filas repetidas (True o False)
    # sum() cuenta cuántas filas están duplicadas
    print("Duplicados:", df.duplicated().sum())

    # Selecciona la columna cn y comprueba si hay códigos repetidos
    # sum() cuenta cuántos valores están repetidos, sin contar la primera aparición
    print("CN repetidos:", df["cn"].duplicated().sum())

    # Selecciona la columna de principios activos
    # value_counts() cuenta cuántas veces aparece cada valor
    # head(10) selecciona los 10 principios activos más frecuentes
    print(df["pactivos"].value_counts().head(10))

    # Cuenta cuántos medicamentos hay de cada forma farmacéutica
    # Por ejemplo: comprimidos, cremas, soluciones...
    print(df["forma_farmaceutica_simplificada"].value_counts())

    # Cuenta cuántos medicamentos hay de cada categoría de genérico
    print(df["generico"].value_counts())



def limpiar_datos(df):
    # Definimos una función que recibe un DataFrame llamado df

    # copy() crea una copia para no modificar el DataFrame original
    df = df.copy()

    # drop_duplicates() elimina las filas completamente repetidas
    # Guardamos el resultado otra vez en df
    df = df.drop_duplicates()

    # select_dtypes(include="object") selecciona columnas de tipo object
    # .columns obtiene sus nombres
    # El for recorre esas columnas una por una
    for columna in df.select_dtypes(include="object").columns:

        # map() aplica una función a cada valor de la columna
        # lambda valor: define una función pequeña sin nombre
        # isinstance(valor, str) comprueba si el valor es texto
        # strip() elimina los espacios al principio y al final
        # else valor: si no es texto, lo deja como estaba
        df[columna] = df[columna].map(
            lambda valor: valor.strip() if isinstance(valor, str) else valor
        )

    # replace() sustituye los textos indicados por pd.NA (valor nulo)
    df = df.replace(["", "Dato no disponible", "N/A"], pd.NA)

    # drop(columns=...) elimina las dos columnas indicadas
    # num_excipientes no tiene información útil
    # Código Nacional contiene información que ya tenemos en cn
    df = df.drop(columns=["num_excipientes", "Código Nacional"])

    # Seleccionamos la columna pactivos
    # replace() sustituye el texto repetido por APREMILAST
    # Guardamos el resultado en la misma columna
    df["pactivos"] = df["pactivos"].replace(
        "APREMILAST, APREMILAST, APREMILAST", "APREMILAST"
    )

    # El for recorre las dos columnas de fechas
    for columna in ["estado_aut", "estado_rev"]:

        # pd.to_datetime() convierte los valores en fechas
        # unit="ms": interpreta los números como milisegundos desde 1970
        # errors="coerce": los valores no válidos pasan a NaT
        # NaT significa que falta una fecha
        df[columna] = pd.to_datetime(
            df[columna], unit="ms", errors="coerce"
        )

    # Recorremos las dos columnas de identificadores
    for columna in ["nregistro", "cn"]:

        # astype("string") convierte los valores a tipo texto
        # Los códigos se tratan como identificadores, no como cantidades
        df[columna] = df[columna].astype("string")

    # Creamos una lista con los nombres de las columnas de precios
    # Así podemos trabajar con ambas utilizando un único for
    precios = [
        "Precio de venta al público con IVA",
        "Precio de referencia"
    ]

    # Recorremos las dos columnas de precios
    for columna in precios:

        # pd.to_numeric() convierte los valores a números
        # errors="coerce": si no se puede convertir, pone NaN
        # NaN representa un valor numérico desconocido
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    # Creamos una lista de columnas que contienen cantidades
    contadores = [
        "palabras_seccion_4_4",
        "numero_tablas",
        "contador_grave"
    ]

    # Recorremos las tres columnas de contadores
    for columna in contadores:

        # Convertimos sus valores a números
        # Los valores no válidos pasan a NaN
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    # precios + contadores une ambas listas de columnas
    # El for recorre todas esas columnas
    for columna in precios + contadores:

        # df[columna] < 0 comprueba qué valores son negativos
        # df.loc[condición, columna] selecciona esas posiciones
        # pd.NA sustituye los valores negativos por nulos
        df.loc[df[columna] < 0, columna] = pd.NA

    # Recorremos las columnas de contadores
    for columna in contadores:

        # dropna() elimina temporalmente los nulos de la comprobación
        # % 1 calcula el resto de dividir cada valor entre 1
        # Si el resto es 0, el número no tiene parte decimal
        # == 0 comprueba si cada número es entero
        # all() comprueba si todos cumplen esa condición
        if (df[columna].dropna() % 1 == 0).all():

            # astype("Int64") convierte la columna a números enteros
            # Int64 permite conservar los valores nulos
            df[columna] = df[columna].astype("Int64")

    # return devuelve el DataFrame después de la limpieza
    return df

def revisar_anomalias(df):
    # Definimos una función que recibe el DataFrame limpio

    # Guardamos el nombre de la columna de precios en una variable
    # Así no tenemos que escribir el nombre completo cada vez
    precio = "Precio de venta al público con IVA"

    # duplicated() identifica filas repetidas
    # sum() cuenta cuántas filas están repetidas
    # \n introduce un salto de línea
    print("\nDuplicados después de limpiar:", df.duplicated().sum())

    # Seleccionamos únicamente la columna cn
    # duplicated() busca códigos repetidos
    # sum() cuenta cuántos hay
    print("CN repetidos:", df["cn"].duplicated().sum())

    # Mostramos un título para la siguiente comprobación
    print("\nValores negativos en precios o contadores:")

    # Creamos una lista con las columnas que queremos revisar
    columnas = [
        precio,
        "Precio de referencia",
        "palabras_seccion_4_4",
        "numero_tablas",
        "contador_grave"
    ]

    # Recorremos cada columna de la lista
    for columna in columnas:

        # df[columna] < 0 comprueba qué valores son negativos
        # Devuelve True para los negativos y False para el resto
        # sum() cuenta los True
        # print() muestra el nombre de la columna y el resultado
        print(columna, (df[columna] < 0).sum())

    # DETECCIÓN DE PRECIOS ATÍPICOS CON EL MÉTODO IQR

    # quantile(0.25) calcula el primer cuartil (Q1)
    # El 25 % de los precios queda por debajo aproximadamente
    q1 = df[precio].quantile(0.25)

    # quantile(0.75) calcula el tercer cuartil (Q3)
    # El 75 % de los precios queda por debajo aproximadamente
    q3 = df[precio].quantile(0.75)

    # Calculamos el rango intercuartílico
    # IQR = tercer cuartil - primer cuartil
    iqr = q3 - q1

    # Calculamos el límite inferior de los precios normales
    minimo = q1 - 1.5 * iqr

    # Calculamos el límite superior de los precios normales
    maximo = q3 + 1.5 * iqr

    # df[precio] < minimo comprueba precios demasiado bajos
    # df[precio] > maximo comprueba precios demasiado altos
    # | significa OR (se cumple una condición o la otra)
    # df[...] filtra las filas que cumplen alguna condición
    # Guardamos esos medicamentos en un nuevo DataFrame
    outliers = df[(df[precio] < minimo) | (df[precio] > maximo)]

    # len(outliers) cuenta las filas del DataFrame de outliers
    print("\nPrecios atípicos para revisar:", len(outliers))

    # Seleccionamos las columnas nombre y precio de los outliers
    # to_string() convierte la tabla en texto para mostrarla completa
    # index=False evita mostrar los índices de las filas
    print(outliers[["nombre", precio]].to_string(index=False))

    # No eliminamos los outliers, solo los identificamos
    # Un precio muy alto no significa necesariamente que sea incorrecto



def analizar_datos(df):
    # Definimos una función que recibe el DataFrame limpio

    # Guardamos el nombre de la columna en una variable
    # Así no tenemos que escribirlo completo cada vez
    precio = "Precio de venta al público con IVA"

    # \n añade un salto de línea antes del texto
    print("\nEstadísticas de precios:")

    # df[precio] selecciona la columna de precios
    # describe() calcula estadísticas como media, mediana,
    # desviación típica, mínimo, máximo y cuartiles
    # print() muestra los resultados por pantalla
    print(df[precio].describe())

    # Mostramos un título para la siguiente tabla
    print("\nPrecios por forma farmacéutica:")

    # groupby() agrupa los medicamentos por forma farmacéutica
    # [precio] selecciona la columna de precios dentro de cada grupo
    # agg() permite calcular varias estadísticas a la vez
    # count: cuenta los precios no nulos de cada grupo
    # mean: calcula el precio medio
    # median: calcula el precio mediano
    print(
        df.groupby("forma_farmaceutica_simplificada")[precio]
        .agg(["count", "mean", "median"])
    )

    # Mostramos un título
    print("\nPrecios de genéricos y no genéricos:")

    # groupby("generico") agrupa según la categoría de genérico
    # [precio] selecciona la columna de precios
    # median() calcula el precio mediano para cada grupo
    print(df.groupby("generico")[precio].median())

    # Mostramos un título para la tabla cruzada
    print("\nTabla cruzada:")

    # pd.crosstab() crea una tabla de frecuencias
    # Primer argumento: categorías que aparecen en las filas
    # Segundo argumento: categorías que aparecen en las columnas
    # Cada celda cuenta los medicamentos de esa combinación
    print(pd.crosstab(
        df["forma_farmaceutica_simplificada"],
        df["generico"]
    ))

    # Creamos una lista con tres columnas numéricas
    # relacionadas con la información de las fichas técnicas
    columnas = [
        "palabras_seccion_4_4",
        "numero_tablas",
        "contador_grave"
    ]

    # df[columnas] selecciona esas tres columnas
    # corr() calcula la correlación entre cada pareja de variables
    # Por defecto utiliza la correlación de Pearson
    # El resultado es una matriz de correlaciones
    print(df[columnas].corr())



def crear_graficos(df):
    # Definimos una función que recibe el DataFrame limpio

    # Guardamos el nombre de la columna de precios
    precio = "Precio de venta al público con IVA"

    # GRÁFICO 1: VALORES NULOS

    # isna() identifica los valores nulos
    # sum() cuenta los nulos de cada columna
    nulos = df.isna().sum()

    # nulos > 0 selecciona columnas que tienen algún nulo
    # sort_values() ordena las columnas según el número de nulos
    # plot(kind="barh") crea un gráfico de barras horizontales
    nulos[nulos > 0].sort_values().plot(kind="barh")

    # Añadimos un título al gráfico
    plt.title("Valores nulos")

    # tight_layout() ajusta los márgenes para que no se corte el texto
    plt.tight_layout()

    # show() muestra el gráfico por pantalla
    plt.show()

    # GRÁFICO 2: PRINCIPIOS ACTIVOS

    # Seleccionamos la columna pactivos
    # value_counts() cuenta las veces que aparece cada principio activo
    # head(10) selecciona los diez más frecuentes
    # sort_values() los ordena de menor a mayor frecuencia
    # plot(kind="barh") crea un gráfico de barras horizontales
    df["pactivos"].value_counts().head(10).sort_values().plot(
        kind="barh"
    )

    # Añadimos título y mostramos el gráfico
    plt.title("Principios activos más frecuentes")
    plt.tight_layout()
    plt.show()

    # GRÁFICO 3: FORMAS FARMACÉUTICAS

    # value_counts() cuenta los medicamentos por forma farmacéutica
    # sort_values() ordena los resultados por frecuencia
    # plot(kind="barh") crea barras horizontales
    df["forma_farmaceutica_simplificada"].value_counts().sort_values().plot(
        kind="barh"
    )

    # Añadimos título, ajustamos márgenes y mostramos
    plt.title("Formas farmacéuticas")
    plt.tight_layout()
    plt.show()

    # GRÁFICO 4: DISTRIBUCIÓN DE PRECIOS

    # df[precio] selecciona la columna de precios
    # dropna() excluye los precios nulos para este gráfico
    # hist() crea un histograma
    # bins=20 divide los precios en 20 intervalos
    df[precio].dropna().hist(bins=20)

    # Añadimos título y nombres de los ejes
    plt.title("Distribución de precios")
    plt.xlabel("Precio (€)")  # Nombre del eje horizontal
    plt.ylabel("Número de medicamentos")  # Nombre del eje vertical
    plt.show()

    # GRÁFICO 5: BOXPLOT DE PRECIOS

    # boxplot() crea un diagrama de caja y bigotes
    # column=precio indica qué columna queremos representar
    # Permite visualizar mediana, cuartiles y posibles outliers
    df.boxplot(column=precio)

    # Añadimos título y nombre del eje vertical
    plt.title("Valores atípicos de precios")
    plt.ylabel("Precio (€)")
    plt.show()

    # GRÁFICO 6: PRECIOS POR FORMA FARMACÉUTICA

    # groupby() agrupa por forma farmacéutica
    # [precio] selecciona los precios de cada grupo
    # median() calcula el precio mediano de cada grupo
    # dropna() elimina los grupos sin precio mediano
    # sort_values() ordena los precios de menor a mayor
    # plot(kind="barh") representa los resultados en barras horizontales
    df.groupby("forma_farmaceutica_simplificada")[precio].median().dropna().sort_values().plot(
        kind="barh"
    )

    # Añadimos título y etiqueta del eje horizontal
    plt.title("Precio mediano por forma farmacéutica")
    plt.xlabel("Precio (€)")
    plt.tight_layout()
    plt.show()

    # GRÁFICO 7: GENÉRICOS POR FORMA FARMACÉUTICA

    # pd.crosstab() cuenta medicamentos por forma y por categoría de genérico
    # plot(kind="barh") crea barras horizontales
    # stacked=True apila las categorías dentro de cada barra
    pd.crosstab(
        df["forma_farmaceutica_simplificada"],
        df["generico"]
    ).plot(kind="barh", stacked=True)

    # Añadimos título, ajustamos los márgenes y mostramos
    plt.title("Genéricos por forma farmacéutica")
    plt.tight_layout()
    plt.show()

    # GRÁFICO 8: EXTENSIÓN DE FICHAS TÉCNICAS

    # Seleccionamos la columna con el número de palabras
    # hist(bins=20) divide los valores en 20 intervalos
    # El histograma muestra cuántos medicamentos hay en cada intervalo
    df["palabras_seccion_4_4"].hist(bins=20)

    # Añadimos título y nombres de los ejes
    plt.title("Palabras de la sección 4.4")
    plt.xlabel("Número de palabras")
    plt.ylabel("Número de medicamentos")
    plt.show()

    # GRÁFICO 9: RELACIÓN ENTRE VARIABLES

    # plt.scatter() crea un gráfico de dispersión
    # Primer argumento: valores del eje X (número de palabras)
    # Segundo argumento: valores del eje Y (contador grave)
    # Cada punto representa un medicamento
    plt.scatter(df["palabras_seccion_4_4"], df["contador_grave"])

    # Añadimos nombres a los ejes y título
    plt.xlabel("Palabras sección 4.4")
    plt.ylabel("Contador grave")
    plt.title("Palabras y contador grave")
    plt.show()

    # GRÁFICO 10: AUTORIZACIONES POR AÑO

    # df["estado_aut"] selecciona las fechas de autorización
    # .dt permite acceder a partes de una fecha
    # .year extrae el año de cada fecha
    # value_counts() cuenta cuántas autorizaciones hay por año
    # sort_index() ordena los años cronológicamente
    # plot() representa los resultados en un gráfico de líneas
    df["estado_aut"].dt.year.value_counts().sort_index().plot()

    # Añadimos título y nombres de los ejes
    plt.title("Autorizaciones por año")
    plt.xlabel("Año")
    plt.ylabel("Número de medicamentos")
    plt.show()



def guardar_datos(df):
    # Definimos una función que recibe el DataFrame limpio

    # to_csv() convierte y guarda el DataFrame en un archivo CSV
    df.to_csv(
        "medicamentos_psoriasis_HU4_limpio.csv",  # Nombre del archivo de salida
        index=False,  # No guardamos los índices como una columna adicional
        encoding="utf-8-sig"  # Permite que Excel reconozca bien las tildes y la ñ
    )

    # Mostramos un mensaje cuando termina de guardar
    print("\nBase de datos limpia guardada correctamente")


def main():
    # Definimos la función principal del programa

    # Guardamos la ruta donde está el Excel original
    # .. significa subir una carpeta en la estructura de directorios
    ruta = "../hu_3/medicamentos_psoriasis_HU3.xlsx"

    # Llamamos a cargar_datos() y le pasamos la ruta del Excel
    # Guardamos el DataFrame resultante en la variable df
    df = cargar_datos(ruta)

    # Llamamos a explorar_datos() para estudiar el dataset original
    # No modificamos los datos, solo mostramos información
    explorar_datos(df)

    # Llamamos a limpiar_datos() para realizar las correcciones
    # Guardamos el resultado limpio en una variable nueva
    df_limpio = limpiar_datos(df)

    # Revisamos duplicados, valores negativos y precios atípicos
    revisar_anomalias(df_limpio)

    # Calculamos estadísticas y correlaciones con el dataset limpio
    analizar_datos(df_limpio)

    # Guardamos el DataFrame limpio en un archivo CSV
    guardar_datos(df_limpio)

    # Generamos las diez gráficas utilizando el DataFrame limpio
    crear_graficos(df_limpio)


# __name__ contiene el nombre del módulo de Python
# Si ejecutamos directamente este archivo, __name__ vale "__main__"
# Si importamos el archivo desde otro programa, esta condición es False
if __name__ == "__main__":

    # Ejecutamos la función principal
    main()
