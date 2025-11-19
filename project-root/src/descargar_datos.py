import requests
import os
import glob
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suprimir advertencias de SSL si es necesario
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- CONFIGURACIÓN ---
URL_DATASET = "https://www.datosabiertos.gob.pe/node/21805/download"
FILENAME_FINAL = "DATASET_Denuncias_Policiales.csv"

# Rutas dinámicas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def actualizar_toda_la_data():
    """Función principal llamada desde el botón de Streamlit."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    reporte = []
    print(f"🚀 Iniciando proceso de actualización...")
    print(f"📂 Directorio de datos: {DATA_DIR}")

    # Nombre de archivo temporal
    temp_filename = f"temp_{int(time.time())}.csv"
    ruta_temp = os.path.join(DATA_DIR, temp_filename)
    ruta_final = os.path.join(DATA_DIR, FILENAME_FINAL)

    # Headers para simular ser un navegador real (Crucial para gob.pe)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    try:
        print(f"⬇️ Descargando desde: {URL_DATASET}")
        
        # Descargamos primero al archivo temporal
        # verify=False ayuda si el certificado SSL del gobierno tiene problemas
        with requests.get(URL_DATASET, headers=headers, stream=True, timeout=120, verify=False) as r:
            r.raise_for_status()
            
            # Verificamos que no nos esté devolviendo un error HTML disfrazado
            content_type = r.headers.get('Content-Type', '')
            if 'text/html' in content_type and int(r.headers.get('Content-Length', 0)) < 15000:
                raise Exception("El servidor devolvió una página web en lugar de un CSV. Posible bloqueo o enlace roto.")

            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0

            with open(ruta_temp, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
        
        print(f"✅ Descarga temporal completada ({downloaded_size / 1024 / 1024:.2f} MB)")

        # --- FASE DE REEMPLAZO SEGURO ---
        # 1. Borrar CSVs antiguos SÓLO AHORA que tenemos el nuevo
        patron = os.path.join(DATA_DIR, "DATASET_Denuncias_Policiales*.csv")
        archivos_antiguos = glob.glob(patron)
        
        for f in archivos_antiguos:
            # No borramos el temporal que acabamos de crear
            if os.path.abspath(f) != os.path.abspath(ruta_temp):
                try:
                    os.remove(f)
                    print(f"🗑️ Eliminado antiguo: {os.path.basename(f)}")
                except Exception as e:
                    print(f"⚠️ No se pudo borrar {os.path.basename(f)}: {e}")

        # 2. Renombrar el temporal al nombre final
        if os.path.exists(ruta_final):
            os.remove(ruta_final) # Asegurar que no estorbe
            
        os.rename(ruta_temp, ruta_final)
        
        msg = f"✓ ¡Datos actualizados con éxito! Nuevo archivo: {FILENAME_FINAL}"
        reporte.append(msg)
        print(msg)
        
    except Exception as e:
        # Si falla, intentamos limpiar el temporal si quedó a medias
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)
            
        err_msg = f"❌ Error crítico: {str(e)}"
        reporte.append(err_msg)
        print(err_msg)

    return reporte

if __name__ == "__main__":
    actualizar_toda_la_data()
