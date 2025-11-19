import requests
import os
from tqdm import tqdm

# --- CONFIGURACIÓN DE LOS RECURSOS ---
# NOTA IMPORTANTE: Los enlaces del Dataset y Metadato en el PDF original 
# apuntan a la página web, no al archivo directo.
# Debes verificar si necesitas actualizarlos con el enlace directo (.zip o .csv).

RECURSOS = {
    # 1. Diccionario de datos
    "Diccionario_Policiales": {
        "url": "https://www.datosabiertos.gob.pe/sites/default/files/DICCIONARIO_DATOS_Denuncias_Policiales.xlsx",
        "filename": "Diccionario_Denuncias_Policiales.xlsx"
    },
    # 2. DataSet Denuncias Policiales (Verifica este enlace)
    "DataSet_2018_2025": {
        # URL de la página del recurso según el PDF (puede requerir cambio por el link directo al .zip)
        "url": "https://www.datosabiertos.gob.pe/dataset/denuncias-policiales/resource/4622d148-94ff-4561-aeb4-11cf273ffdbe" 
    },
    # 3. Metadato (Verifica este enlace)
    "Metadato_Octubre_2025": {
        "url": "https://www.datosabiertos.gob.pe/dataset/denuncias-policiales/resource/4622d148-94ff-4561-aeb4-11cf273ffdbe"
    }
}

# Directorio donde se guardarán los archivos
DOWNLOAD_DIR = "datos_policiales"

# --- FUNCIÓN DE DESCARGA ---
def download_file(url, filename):
    """Descarga un archivo grande con barra de progreso (streaming)."""
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    print(f"[{filename}] Iniciando descarga desde: {url}")
    
    try:
        # Usamos stream=True para descargar eficientemente
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status() # Error si el link no funciona (404, 500)
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 KB
        
        with open(filepath, 'wb') as file:
            with tqdm(total=total_size, unit='iB', unit_scale=True, desc=filename) as progress_bar:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
                    
        print(f"[{filename}] ✓ ¡Descarga completada y guardada en: {filepath}!")
        
    except requests.exceptions.RequestException as e:
        print(f"[{filename}] X ERROR al descargar {url}: {e}")
        print(" - Sugerencia: El enlace directo puede haber cambiado. Verifica la URL.")
    except Exception as e:
        print(f"[{filename}] Ocurrió un error inesperado: {e}")

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # 1. Crear directorio si no existe
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"Directorio '{DOWNLOAD_DIR}' creado.")
        
    # 2. Iterar y descargar cada recurso
    for name, data in RECURSOS.items():
        download_file(data["url"], data["filename"])
        
    print("-" * 50)

    print(f"Proceso finalizado. Revisa el directorio '{DOWNLOAD_DIR}'.")
