import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup  # Nueva librería para scraping

# --- CONFIGURACIÓN DE LOS RECURSOS (URLs PERMANENTES) ---
RECURSOS = {
    "Diccionario_Policiales": {
        "page_url": "https://www.datosabiertos.gob.pe/dataset/denuncias-policiales/resource/4622d148-94ff-4561-aeb4-11cf273ffdbe",
        "filename": "DICCIONARIO_DATOS_Denuncias_Policiales.xlsx" # O .csv según lo que baje
    },
    "DataSet_2018_2025": {
        "page_url": "https://www.datosabiertos.gob.pe/dataset/denuncias-policiales/resource/64c01d53-4402-4e5a-936a-4bce5b3d1008",
        "filename": "DATASET_Denuncias_Policiales.csv" # Nombre genérico para facilitar la carga
    },
    "Metadato_Octubre_2025": {
        "page_url": "https://www.datosabiertos.gob.pe/dataset/denuncias-policiales/resource/83c992fc-145c-4916-8dac-ad39fad9d000",
        "filename": "METADATO_Denuncias_Policiales.docx"
    }
}

DOWNLOAD_DIR = "project-root/data" # Asegúrate que coincida con tu estructura

def obtener_url_descarga_real(page_url):
    """
    Entra a la página del recurso y busca el botón de descarga real.
    El portal de datos de Perú usa CKAN, el botón suele tener la clase 'resource-url-analytics'.
    """
    try:
        print(f"   Refrescando enlace desde: {page_url}...")
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Estrategia 1: Buscar por la clase específica de CKAN (la plataforma que usa gob.pe)
        boton = soup.find('a', class_='resource-url-analytics')
        
        # Estrategia 2: Si falla, buscar un link que diga "Descargar"
        if not boton:
            boton = soup.find('a', string="Descargar")
            
        if boton and 'href' in boton.attrs:
            return boton['href']
        else:
            raise Exception("No se encontró el botón de descarga en el HTML.")
            
    except Exception as e:
        print(f"   Error al hacer scraping de la URL: {e}")
        return None

def download_file(url, filename, folder):
    filepath = os.path.join(folder, filename)
    
    try:
        # Usamos stream=True para descargar eficientemente
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as file:
            # Si streamlit está corriendo, no veremos la barra tqdm en la consola, 
            # pero no afecta la funcionalidad.
            for data in response.iter_content(1024):
                file.write(data)
                    
        return True, f"Descargado: {filename}"
        
    except Exception as e:
        return False, f"Error descargando {filename}: {str(e)}"

def actualizar_toda_la_data():
    """Función principal para ser llamada desde Streamlit"""
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    reporte = []
    
    for key, info in RECURSOS.items():
        # 1. Obtener URL real (Scraping)
        real_url = obtener_url_descarga_real(info["page_url"])
        
        if real_url:
            # 2. Descargar
            success, msg = download_file(real_url, info["filename"], DOWNLOAD_DIR)
            reporte.append(msg)
        else:
            reporte.append(f"Fallo al obtener enlace para {key}")
            
    return reporte

# Bloque para probarlo individualmente
if __name__ == "__main__":
    print("Iniciando actualización manual...")
    resultados = actualizar_toda_la_data()
    for r in resultados:
        print(r)
