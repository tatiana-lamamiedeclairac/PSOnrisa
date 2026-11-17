import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

#Para que lea el .env
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Cargar el csv limpio de la HU5
df = pd.read_csv("../hu_5/medicamentos_psoriasis_HU5_limpio.csv")
# Comprobar que se ha cargado correctamente
print(df.shape)
print(df.head())

# Configurar la conexión con MySQL. 
# URL.create construye la dirección que necesita SQLAlchemy para 
# conectarse a MySQL
url = URL.create(
    "mysql+pymysql",
    # Obtener las credenciales de MySQL
    username=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    host="localhost",
    port=3306,
    database="medicamentos_psoriasis"
)

# Crear el motor de conexión. La función crea un objeto que contiene
# la configuración necesaria para conectarse a MySQL
engine = create_engine(url)

# Comprobar la conexión
with engine.connect() as conexion:
    print("Conexión correcta con MySQL")


# Cargar el DataFrame en una tabla de MySQL
df.to_sql(
    name="medicamentos",
    con=engine,
    if_exists="replace",
    index=False
)

print("Datos cargados correctamente en MySQL")