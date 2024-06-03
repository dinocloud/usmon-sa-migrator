import subprocess
import os
import argparse
import json
from datetime import datetime
from collections import deque

# Función para leer la lista de containers desde un archivo JSON
def leer_containers_desde_json(ruta_json):
    try:
        with open(ruta_json, 'r') as archivo:
            containers = json.load(archivo)
        return containers
    except Exception as e:
        print(f"Error al leer el archivo JSON: {e}", flush=True)
        exit(1)

# Directorio de logs
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Crear un analizador de argumentos
parser = argparse.ArgumentParser(description="Script para sincronizar y generar logs con rclone.")
parser.add_argument("--transfers", type=int, default=4, help="Número de transferencias simultáneas (por defecto: 4)")
parser.add_argument("--checkers", type=int, default=8, help="Número de verificadores simultáneos (por defecto: 8)")
parser.add_argument("--bucket", type=str, required=True, help="Nombre de S3 bucket")
parser.add_argument("--containers_json", type=str, required=True, help="Ruta al archivo JSON que contiene la lista de containers")
parser.add_argument("--debug", action='store_true', help="Activar salida detallada de rclone")
args = parser.parse_args()

# Leer la lista de containers desde el archivo JSON
containers = leer_containers_desde_json(args.containers_json)

# Registrar la hora de inicio del script
script_start_time = datetime.now()

print(f"Inicio del script: {script_start_time}", flush=True)

# Función para ejecutar el comando rclone y generar logs
def sync_and_log(valor):
    comando = f"rclone sync AZStorageAccount:{valor} s3:{args.bucket}/{valor} --transfers {args.transfers} --checkers {args.checkers}"
    if args.debug:
        comando += " --verbose"

    log_file = os.path.join(log_dir, f"sync_{valor}.log")

    # Registrar la hora de inicio
    start_time = datetime.now()

    # Usar deque para mantener las últimas 100 líneas en memoria
    last_100_lines = deque(maxlen=100)

    process = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            last_100_lines.append(output)
            # Escribir las líneas del deque al archivo de log
            with open(log_file, "w") as log:
                log.writelines(last_100_lines)

    process.communicate()
    if process.returncode != 0:
        print(f"Error al sincronizar {valor}. Terminando el script.", flush=True)
        exit(1)

    # Registrar la hora de finalización
    end_time = datetime.now()

    # Calcular el tiempo transcurrido
    elapsed_time = end_time - start_time

    print(f"Sincronización y log para {valor} completados en {elapsed_time}.", flush=True)

# Ejecutar el comando para cada valor y generar logs
try:
    for valor in containers:
        sync_and_log(valor)
except Exception as e:
    print(e, flush=True)
    print("Terminando el script debido a un error.", flush=True)

# Registrar la hora de finalización del script
script_end_time = datetime.now()

# Calcular el tiempo total de ejecución
script_elapsed_time = script_end_time - script_start_time

print(f"Todas las sincronizaciones han sido completadas en {script_elapsed_time}", flush=True)
print(f"Fin del script: {script_end_time} \n", flush=True)
