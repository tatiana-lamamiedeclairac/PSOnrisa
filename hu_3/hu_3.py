import pandas as pd

df_medicamentos= pd.read_excel("../hu_2_webscrapping/medicamentos_con_metricas.xlsx")
df_nomenclator = pd.read_excel("nomenclator.xls")

# Tenemos que mirar cómo se llaman las columnas
# print(df_medicamentos.columns)
# print(df_nomenclator.columns)

columnas = [
    "Código Nacional",
    "Estado", 
    "Precio de venta al público con IVA",
    "Precio de referencia",
    "Tratamiento de larga duración",
    "Especial control médico"
]

# Del df del ministerio nos quedamos solo con las columnas necesarias
df_nomenclator = df_nomenclator[columnas]

df_medicamentos["cn"] = df_medicamentos["cn"].astype(str)
df_nomenclator["Código Nacional"] = df_nomenclator["Código Nacional"].astype(str)

# Al hacer left_on="cn", le estamos diciendo que la columna que se
# debe utilizar para buscar coincidencias en nuestro excel es cn, 
# y al hacer right_on="Código Nacional" estamos diciendo que la columna
# equivalente es "Código Nacional" para el excel nomenclator
# how="left" es para mantener todos los medicamentos que tenía nuestro excel
df_final = pd.merge(
    df_medicamentos,
    df_nomenclator,
    left_on="cn",
    right_on="Código Nacional",
    how="left"
)

df_final.to_excel(
    "medicamentos_psoriasis_HU3.xlsx",
    index=False
)

print("El excel ha sido creado correctamente")