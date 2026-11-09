import os
# Limitamos los hilos de OpenMP para evitar un aviso
# de consumo de memoria de K-Means con MKL en Windows.
os.environ["OMP_NUM_THREADS"] = "2"
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
#Si hubiese nulos en las variables que he usado para el modelo: from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
import seaborn as sns #para el gráfico
import matplotlib.pyplot as plt#para el gráfico
#1 CARGAMOS LOS DATOS LIMPIOS DE LA HU-4
df = pd.read_csv("medicamentos_psoriasis_HU4_limpio.csv")


#2 DEFINIMOS LAS VARIABLES
variables_excluir = [
    "nregistro", #Es el identificador del medicamento
    "nombre", #sirve para identificar el medicamento
    "pactivos", #Podría codificarlos pero hay demasiados diferentes
    "labtitular", #Si la usasemos agruparia por laboratorio y no por características del medicamento
    "labcomercializador", #Lo mismo que la anterior
    "cn", #identificador
    "dosis", #Se mezclan unidades y no se pueden comparar directamente
    "url_html_ficha_tecnica", #Son enlaces              
    "url_foto_materiales", #Son enlaces
    "Estado", #Tiene 235 nulos, teniendo 370 medicamentos
    "Precio de referencia", #Tiene 251 nulos
    "Precio de venta al público con IVA", #Tiene 235 nulos
    "Especial control médico", #Tiene 235 nulos
    "Tratamiento de larga duración", #Tiene 235
    "estado_aut",  # Estado de autorización del medicamento (son fechas)
    "estado_rev",  # Estado de revisión (son fechas)
    "medicamento_huerfano", #    Solo tiene 0 
    "num_registros_atc", #Se excluye porque presenta muy poca variabilidad (367 de los 370 medicamentos tienen el mismo valor) y únicamente contabiliza los registros ATC, sin aportar información suficiente para diferenciar los perfiles farmacológicos. Además, su inclusión provocaba la formación de un clúster aislado de solo 3 medicamentos.   
    "vias_administracion"  #Como da mas o menos la misma info que la de la forma farmaceutica 
]
variables = [
    "num_principios_activos",
    "palabras_seccion_4_4",
    "numero_tablas",
    "contador_grave",   
]
variables_binarias = [
    "comerc", #ESTAS SON BINARIAS
    "requiere_receta",
    "generico",
    "afecta_conduccion",
    "triangulo_negro",
    "biosimmilar",
]
# Variables categóricas que podríamos transformar a numéricas
variables_categoricas_pasar_numericas = [
    "forma_farmaceutica_simplificada"  # Comprimidos, cápsulas, soluciones, etc.

]


#3 COMPROBAR LAS COLUMNAS
columnas_modelo = (
    variables
    + variables_binarias
    + variables_categoricas_pasar_numericas
)

faltantes = set(columnas_modelo) - set(df.columns)

if faltantes:
    raise ValueError(f"Faltan columnas en el CSV: {faltantes}")


#4 PREPARAR VARIABLES NUMÉRICAS
# Convertimos las variables seleccionadas a tipo numérico.
# Si alguna contiene un valor no convertible, se genera un error.
X_numericas = df[variables].apply(
    pd.to_numeric,
    errors="raise"
)

# Comprobamos que no existen valores ausentes antes del entrenamiento.
# Al no haber nulos, no es necesario aplicar imputación.
if X_numericas.isna().any().any():
    raise ValueError("Hay nulos en las variables numéricas")

#No hay nulos si los hubiese
#imputador = SimpleImputer(strategy="median")
#X_numericas = pd.DataFrame(
#    imputador.fit_transform(X_numericas),
#    columns=variables,
#    index=df.index
#)

# Estandarizamos las variables para evitar que aquellas con valores
# más elevados tengan mayor influencia en las distancias de K-Means.
escalador = StandardScaler()

X_numericas = pd.DataFrame(
    escalador.fit_transform(X_numericas),
    columns=variables,
    index=df.index
)

#5 PREPARAR VARIABLES BINARIAS
# Las variables binarias representan características del medicamento
# mediante valores 0 y 1.
# Unificamos su codificación y comprobamos que no existen
# valores distintos de 0 y 1 ni valores ausentes.
X_binarias = df[variables_binarias].copy()
for columna in variables_binarias:
    X_binarias[columna] = X_binarias[columna].replace({
        "SI": 1,
        "NO": 0,
        "Sí": 1,
        "No": 0,
        "True": 1,
        "False": 0
    })

    X_binarias[columna] = pd.to_numeric(
        X_binarias[columna],
        errors="coerce"
    )
# Comprobamos que las variables binarias solo contienen 0 y 1,
# sin valores nulos ni categorías incorrectas.

for columna in variables_binarias:
    valores = set(X_binarias[columna].unique())

    if not valores.issubset({0, 1}):
        raise ValueError(
            f"Valores no válidos en {columna}: {valores}"
        )

#No hay nulos, si los hubiese:
#Imputamos con la moda si hay valores ausentes
#for columna in variables_binarias:
#   moda = X_binarias[columna].mode(dropna=True)
#
#    if moda.empty:
#        raise ValueError(
#            f"La columna {columna} no tiene valores válidos"
#        )
#
#    X_binarias[columna] = X_binarias[columna].fillna(
#        moda.iloc[0]
#    )

X_binarias = X_binarias.astype(int)


# 6 CODIFICAR LA FORMA FARMACÉUTICA

# Agrupamos las 13 formas farmacéuticas originales en 5 categorías
# generales para reducir la dimensionalidad y facilitar la
# interpretación de los clústeres.
#

mapa_formas = {
    "INYECTABLE": "INYECTABLE",
    "INYECTABLE PERFUSION": "INYECTABLE",

    "COMPRIMIDO": "ORAL_SOLIDO",
    "CAPSULA": "ORAL_SOLIDO",

    "SOLUCION/SUSPENSION GOTAS ORALES": "ORAL_LIQUIDO",
    "SOLUCIÓN/SUSPENSIÓN ORAL": "ORAL_LIQUIDO",

    "CREMA": "TOPICO",
    "POMADA": "TOPICO",
    "GEL": "TOPICO",
    "LIQUIDO USO TOPICO": "TOPICO",
    "CHAMPU": "TOPICO",
    "EMULSION": "TOPICO",

    "APÓSITO": "OTROS"
}

# Crear una nueva variable sin modificar la original
formas = df["forma_farmaceutica_simplificada"].map(
    mapa_formas
)

# Comprobar que no quedan categorías sin clasificar
sin_clasificar = (
    df.loc[
        df["forma_farmaceutica_simplificada"].notna()
        & formas.isna(),
        "forma_farmaceutica_simplificada"
    ]
    .unique()
)

if len(sin_clasificar) > 0:
    raise ValueError(
        f"Formas sin clasificar: {sin_clasificar}"
    )

# Tratar valores ausentes
formas = formas.fillna("DESCONOCIDA")

# Aplicamos One-Hot Encoding, creando una columna binaria
# por cada categoría, sin introducir un orden artificial entre ellas.
X_categoricas = pd.get_dummies(
    formas,
    prefix="forma",
    dtype=int
)

print(X_categoricas.columns)

# 7. CONSTRUIR LA MATRIZ FINAL PARA K-MEANS

X = pd.concat(
    [X_numericas, X_binarias, X_categoricas],
    axis=1
)

print("Dimensiones de X:", X.shape)
print("Nulos en X:", X.isna().sum().sum())
print("Variables del modelo:")
print(X.columns.to_list())



#8 ELEGIR EL NÚMERO DE CLÚSTERES
# Entrenamos modelos K-Means con K entre 2 y 10.
# Para cada modelo calculamos:
# - Silhouette Score: separación y cohesión de los clústeres.
# - Inercia: suma de las distancias cuadráticas a los centroides.
# - Tamaños: número de medicamentos asignados a cada grupo.
#
# Guardamos los modelos en fits para reutilizar el seleccionado
# sin necesidad de volver a entrenarlo.
fits = []
resultados = []

for k in range(2, 11):

    modelo = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    etiquetas = modelo.fit_predict(X)
    # Guardamos el modelo entrenado
    fits.append(modelo)
    tamanos = pd.Series(etiquetas).value_counts().sort_index()

    resultados.append({
        "K": k,
        "Silhouette": silhouette_score(X, etiquetas),
        "Inercia": modelo.inertia_,
        "Tamaños_clusters": tamanos.to_list()
    })

resultados_df = pd.DataFrame(resultados)

print("\nComparación de diferentes valores de K:")
print(resultados_df.to_string(index=False))

#9 SELECCIONAR EL MODELO DEFINITIVO
# Elegimos K=3 por ofrecer un equilibrio entre Silhouette Score
# e interpretabilidad de los grupos.
# Aunque K superiores obtienen mejores puntuaciones, generan
# un mayor número de clústeres que complica su interpretación.

k_elegido = 3  # Valor elegido tras analizar las métricas

# Recuperamos el modelo ya entrenado
# Como el bucle empieza en K=2, su posición es K-2.
kmeans = fits[k_elegido - 2]

# Añadimos la clasificación al DataFrame
# Asignamos a cada medicamento el clúster correspondiente
df["cluster"] = kmeans.labels_

print("\nNúmero de medicamentos por clúster:")
print(df["cluster"].value_counts().sort_index())


#10 EVALUAR EL MODELO


if 1 < df["cluster"].nunique() < len(df):
    puntuacion = resultados_df.loc[
    resultados_df["K"] == k_elegido,
    "Silhouette"].iloc[0]

    print("\nSilhouette Score:", round(puntuacion, 3))


#11 ANALIZAR LOS CLÚSTERES
# Calculamos las medias de las variables numéricas para conocer
# las características predominantes de cada grupo.
#


print("\nMedia de las variables numéricas:")
print(
    df.groupby("cluster")[variables]
    .mean()
    .round(2)
    .to_string()
)
# En las variables binarias, la media representa la proporción
# de medicamentos que tienen valor 1
print("\nProporción de variables binarias:")
print(
    df.groupby("cluster")[variables_binarias]
    .mean()
    .round(2)
    .to_string()
)

#
# Analizamos también el porcentaje de cada forma farmacéutica
# dentro de los clústeres para facilitar su interpretación.
print("\nFormas farmacéuticas agrupadas por clúster:")

print(
    pd.crosstab(
        df["cluster"],
        formas,
        normalize="index"
    ).mul(100).round(1).to_string()
)

print(df[variables].corr().round(2).to_string())

# 12. ASIGNAR NOMBRES A LOS CLÚSTERES

# Los nombres se asignan tras analizar las características
# predominantes de cada grupo.

nombres_clusters = {
    0: "Múltiples principios activos",
    1: "Monocomponente de perfil general",
    2: "Inyectables con fichas extensas"
}

df["tipo_medicamento"] = df["cluster"].map(nombres_clusters)


# Comprobamos que todos los medicamentos tienen clasificación
if df["tipo_medicamento"].isna().any():
    raise ValueError("Hay medicamentos sin clasificar")

print("Dimensiones del CSV final:", df.shape)
#13 GUARDAR EL CSV FINAL
df.to_csv(
    "medicamentos_psoriasis_HU5_limpio.csv",
    index=False,
    encoding="utf-8-sig"
)



print("CSV guardado correctamente")


#14 VISUALIZACIÓN DE LOS CLÚSTERES

# Representamos los medicamentos según el número de principios
# activos y la extensión de la sección 4.4, utilizando colores
# para diferenciar los clústeres.
#
# La gráfica muestra únicamente dos variables, aunque K-Means
# ha utilizado las 15 características seleccionadas.


plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=df,
    x="num_principios_activos",
    y="palabras_seccion_4_4",
    hue="tipo_medicamento",
    palette="Set2",
    alpha=0.7
)

plt.title("Segmentación de medicamentos para la psoriasis")
plt.xlabel("Número de principios activos")
plt.ylabel("Palabras de la sección 4.4")
plt.legend(title="Perfil del medicamento")
plt.tight_layout()
plt.show()