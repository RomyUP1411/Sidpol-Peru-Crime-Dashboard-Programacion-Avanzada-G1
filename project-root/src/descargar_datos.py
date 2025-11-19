import requests
import os
import glob

# --- CONFIGURACIÓN ---
# URL directa que me proporcionaste
URL_DATASET = "https://www.datosabiertos.gob.pe/node/21805/download"

# Nombre fijo para el archivo local. Usaremos siempre este nombre para que el Dashboard sepa cuál leer.
FILENAME_LOCAL = "DATASET_Denuncias_Policiales.csv"

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def limpiar_datasets_antiguos():
    """Borra CSVs antiguos para asegurar que leemos el nuevo."""
    patron = os.path.join(DATA_DIR, "DATASET_Denuncias_Policiales*.csv")
    archivos = glob.glob(patron)
    for f in archivos:
        try:
            os.remove(f)
            print(f"   🗑️ Archivo antiguo eliminado: {os.path.basename(f)}")
        except Exception as e:
            print(f"   ⚠️ No se pudo eliminar {os.path.basename(f)}: {e}")

def actualizar_toda_la_data():
    """Función principal llamada desde el botón de Streamlit."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    reporte = []
    print(f"Iniciando actualización desde: {URL_DATASET}")

    try:
        # 1. Limpieza previa (opcional, pero recomendado para evitar duplicados)
        limpiar_datasets_antiguos()

        # 2. Descarga
        ruta_destino = os.path.join(DATA_DIR, FILENAME_LOCAL)
        
        # Usamos stream para descarga eficiente
        with requests.get(URL_DATASET, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(ruta_destino, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        
        msg = f"✓ Datos actualizados correctamente: {FILENAME_LOCAL}"
        reporte.append(msg)
        print(msg)
        
    except Exception as e:
        err_msg = f"❌ Error crítico descargando datos: {str(e)}"
        reporte.append(err_msg)
        print(err_msg)

    return reporte

if __name__ == "__main__":
    actualizar_toda_la_data()
