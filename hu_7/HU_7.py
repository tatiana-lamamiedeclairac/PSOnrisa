
import subprocess

# Importamos sys para acceder al ejecutable de Python
# y poder finalizar el programa cuando haya errores
import sys
# Importamos logging para registrar los eventos,
# ejecuciones correctas y errores en un archivo LOG
import logging
# Importamos Path para trabajar con rutas de archivos
# y carpetas de manera sencilla
from pathlib import Path
# Importamos datetime para obtener la fecha actual
# y utilizarla en el nombre del archivo LOG
from datetime import datetime
# Importamos load_dotenv para cargar las variables
# de entorno guardadas en el archivo .env
from dotenv import load_dotenv
import os

# CAMBIOS REALIZADOS PARA PODER EJECUTAR LA HU7:
# En HU5 hemos cambiado la ruta para que lea directamente
# el CSV limpio generado en la carpeta HU4:
# df = pd.read_csv("../hu_4/medicamentos_psoriasis_HU4_limpio.csv")
#
# En HU3 y HU6 también hemos adaptado las rutas de los archivos
# para que las diferentes historias de usuario estén conectadas.
#
# En HU6 hemos cambiado la conexión con MySQL para que
# utilice el usuario y la contraseña definidos en el .env.
# De esta manera no tenemos que introducirlos por terminal.

# 1. RUTA PRINCIPAL DEL PROYECTO
# __file__ indica la ubicación del archivo HU_7.py
# resolve() obtiene su ruta absoluta
# parent accede a la carpeta hu_7
# parent.parent sube otro nivel hasta la carpeta PSOnrisa
BASE_DIR = Path(__file__).resolve().parent.parent
# Cargar las variables del archivo .env
load_dotenv(BASE_DIR / ".env")

# 2. CONFIGURACIÓN DE LOGS
LOG_DIR = BASE_DIR / "hu_7" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# datetime.now() obtiene la fecha y hora actuales
# strftime() convierte la fecha en una cadena de texto
# con el formato año-mes-día, por ejemplo 2026-11-17
fecha = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOG_DIR / f"PSOnrisa_psoriasis_{fecha}.log"

# Configuramos la librería logging
logging.basicConfig(
    filename=LOG_FILE,# filename indica dónde se guardarán los registros
    level=logging.INFO,    # level=logging.INFO registra mensajes de nivel INFO, WARNING, ERROR y CRITICAL
    format="%(asctime)s | %(levelname)s | %(message)s",
    # format establece el formato de cada registro:
    # asctime: fecha y hora del evento
    # levelname: nivel del mensaje (INFO, ERROR, etc.)
    # message: descripción del evento registrado
    encoding="utf-8"
    # encoding permite guardar caracteres especiales,
    # como tildes y la letra ñ
)

# 3. ORDEN DE EJECUCIÓN DE LAS HU
# Creamos una lista llamada PROCESOS
# Cada elemento es una tupla con dos valores:
# 1. El nombre de la historia de usuario
# 2. La ruta relativa del archivo Python que ejecutaremos
#
# El orden de la lista determina el orden de ejecución
# de las diferentes historias de usuario
PROCESOS = [
    ("HU1 - Extracción",
     "hu_1_extraccion/hu_1_extraccion.py"),

    ("HU2 - Webscraping",
     "hu_2_webscrapping/hu_2_webscraping.py"),

    ("HU3 - Transformación",
     "hu_3/hu_3.py"),

    ("HU4 - Limpieza y EDA",
     "hu_4/eda.py"),

    ("HU5 - Clustering",
     "hu_5/HU5.py"),

    ("HU6 - SQL",
     "hu_6_sql/excel_a_mysql.py")
]

# 4. FUNCIÓN PRINCIPAL DE EJECUCIÓN
def ejecutar_proyecto():
    # Registramos en el LOG el inicio de la ejecución
    logging.info("===== INICIO DEL PROYECTO =====")

    for nombre, archivo in PROCESOS:

        ruta = BASE_DIR / archivo

        logging.info(f"Iniciando {nombre}")
        print(f"Ejecutando {nombre}...")

        try:
            if not ruta.is_file():
                raise FileNotFoundError(
                    f"No existe el archivo: {ruta}"
                )

            # Ejecutamos el script correspondiente
            resultado = subprocess.run(
                # sys.executable utiliza el mismo intérprete
                # de Python con el que se ejecuta HU7
                # str(ruta) convierte la ruta en texto
                [sys.executable, str(ruta)],
                                # cwd establece la carpeta de trabajo
                # del script que estamos ejecutando
                # ruta.parent obtiene la carpeta del archivo
                # Esto permite utilizar las rutas relativas
                # que hemos configurado en las distintas HU
                cwd=ruta.parent,
                # capture_output=True captura lo que el script
                # escribe por pantalla y sus mensajes de error
                capture_output=True,
                text=True,# text=True devuelve la salida del proceso como texto en lugar de bytes
                check=True #comprueba si el proceso ha terminado correctamente. 
                #Si devuelve un código distinto de 0,
                #lanza una excepción CalledProcessError
            )

            # stdout contiene la salida normal del script
            # Comprobamos si se ha generado algún mensaje
            if resultado.stdout:
                # Guardamos esa salida en el archivo LOG
                # utilizando el nivel INFO
                logging.info(resultado.stdout)
            # stderr contiene los mensajes enviados
            # a la salida de errores del script
            if resultado.stderr:
                # Guardamos esos mensajes en el LOG
                # utilizando el nivel WARNIN
                logging.warning(resultado.stderr)
            # Si el proceso llega hasta aquí, significa
            # que el script ha terminado con código 0
            # Registramos su finalización en el LO
            logging.info(f"{nombre} finalizada correctamente")
            print(f"{nombre} completada correctamente")

        except subprocess.CalledProcessError as error:
            logging.error(
                f"Fallo en {nombre}. "
                f"Codigo: {error.returncode}. "
                f"Salida: {error.stdout}. "
                f"Error: {error.stderr}"
            )
            # raise vuelve a lanzar la excepción
            # para detener la ejecución del proyecto
            # Así evitamos ejecutar las siguientes HU
            # si una de las anteriores ha fallado
            raise
        # Capturamos otros posibles errores,
        # como un archivo que no existe
        except Exception:
            logging.exception(f"Error en {nombre}")
            raise

    logging.info("===== PROYECTO FINALIZADO =====")
    print("Todas las HU ejecutadas correctamente")

# __name__ contiene el nombre del módulo de Python
# Si ejecutamos directamente HU_7.py,
# __name__ tendrá el valor "__main__"
# Esto evita que la ejecución comience automáticamente
# si importamos este archivo desde otro programa
if __name__ == "__main__":
    try:
        ejecutar_proyecto()
    except Exception:
        logging.exception("Ejecución interrumpida")
        print(f"Error. Consulta el LOG: {LOG_FILE}")
        # sys.exit(1) termina el programa
        # El código 1 indica que ha finalizado con error
        # Esto permite que el Programador de Tareas
        # detecte que la ejecución no ha sido correcta
        sys.exit(1)

