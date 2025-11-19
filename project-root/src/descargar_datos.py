import glob
import os
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suprimir advertencias de SSL (el portal a veces presenta certificados problemáticos)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- CONFIGURACIÓN ---
URL_DATASET_PAGE = "https://www.datosabiertos.gob.pe/node/21805"
FILENAME_FALLBACK = "DATASET_Denuncias_Policiales.csv"

# Rutas dinámicas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Headers para simular navegador real
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


def _find_csv_url(session: requests.Session) -> str:
    """Encuentra el primer enlace a CSV en la página del dataset."""
    resp = session.get(URL_DATASET_PAGE, headers=headers, timeout=30, verify=False)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    link = soup.find("a", href=lambda h: h and ".csv" in h)
    if not link or not link.get("href"):
        raise RuntimeError("No se encontró enlace CSV en la página del dataset")
    return urljoin(URL_DATASET_PAGE, link["href"])


def _nombre_archivo_final(resp: requests.Response) -> str:
    """Obtiene nombre desde Content-Disposition si viene; si no, usa fallback."""
    cd = resp.headers.get("content-disposition", "")
    if "filename=" in cd:
        parte = cd.split("filename=")[-1]
        nombre = parte.strip('";\' ')
        return nombre or FILENAME_FALLBACK
    return FILENAME_FALLBACK


def actualizar_toda_la_data():
    """Descarga el CSV más reciente desde datosabiertos.gob.pe y lo guarda en data/."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    reporte = []
    print("Iniciando proceso de actualización...")
    print(f"Directorio de datos: {DATA_DIR}")

    temp_filename = f"temp_{int(time.time())}.csv"
    ruta_temp = os.path.join(DATA_DIR, temp_filename)

    try:
        with requests.Session() as session:
            csv_url = _find_csv_url(session)
            print(f"Descargando desde: {csv_url}")

            with session.get(csv_url, headers=headers, stream=True, timeout=120, verify=False) as r:
                r.raise_for_status()
                ruta_final = os.path.join(DATA_DIR, _nombre_archivo_final(r))

                downloaded_size = 0
                with open(ruta_temp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

        print(f"Descarga temporal completada ({downloaded_size / 1024 / 1024:.2f} MB)")

        # Reemplazo seguro: eliminar CSVs antiguos que coincidan con el patrón
        patron = os.path.join(DATA_DIR, "DATASET_Denuncias_Policiales*.csv")
        archivos_antiguos = glob.glob(patron)
        for fpath in archivos_antiguos:
            if os.path.abspath(fpath) != os.path.abspath(ruta_temp):
                try:
                    os.remove(fpath)
                    print(f"Eliminado antiguo: {os.path.basename(fpath)}")
                except Exception as e:
                    print(f"No se pudo borrar {os.path.basename(fpath)}: {e}")

        os.replace(ruta_temp, ruta_final)

        msg = f"Datos actualizados con éxito. Nuevo archivo: {os.path.basename(ruta_final)}"
        reporte.append(msg)
        print(msg)

    except Exception as e:
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)

        err_msg = f"Error crítico: {str(e)}"
        reporte.append(err_msg)
        print(err_msg)

    return reporte


if __name__ == "__main__":
    actualizar_toda_la_data()
