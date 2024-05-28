import subprocess
import os
from datetime import datetime
import argparse

# Lista de valores
valores = [12500, 3300, 4700, 66700]

# Directorio de logs
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Crear un analizador de argumentos
parser = argparse.ArgumentParser(description="Script para sincronizar y generar logs con rclone.")
parser.add_argument("--transfers", type=int, default=8, help="Número de transferencias simultáneas (por defecto: 8)")
parser.add_argument("--checkers", type=int, default=16, help="Número de verificadores simultáneos (por defecto: 16)")
parser.add_argument("--bucket", type=str, required=True, help="Nombre de S3 bucket")
args = parser.parse_args()

# Registrar la hora de inicio del script
script_start_time = datetime.now()

print(f"Inicio del script: {script_start_time}")

# Función para ejecutar el comando rclone y generar logs
def sync_and_log(valor):
    comando = f"rclone sync AZStorageAccount:{valor} s3:{args.bucket}/{valor} --transfers {args.transfers} --checkers {args.checkers} --verbose"
    log_file = os.path.join(log_dir, f"sync_{valor}.log")

    # Registrar la hora de inicio
    start_time = datetime.now()

    with open(log_file, "w") as log:
        process = subprocess.Popen(comando, shell=True, stdout=log, stderr=log)
        process.communicate()

    # Registrar la hora de finalización
    end_time = datetime.now()

    # Calcular el tiempo transcurrido
    elapsed_time = end_time - start_time

    print(f"Sincronización y log para {valor} completados en {elapsed_time}.")

# Ejecutar el comando para cada valor y generar logs
for valor in valores:
    sync_and_log(valor)

# Registrar la hora de finalización del script
script_end_time = datetime.now()

# Calcular el tiempo total de ejecución
script_elapsed_time = script_end_time - script_start_time

print(f"Todas las sincronizaciones han sido completadas en {script_elapsed_time}")
print(f"Fin del script: {script_end_time} \n")
