import pandas as pd
import sqlite3
from pathlib import Path

# --- CONFIGURACIÓN DE RUTAS Y NOMBRES ---
# ¡AJUSTA data_dir SEGÚN LA ESTRUCTURA REAL DE TU REPOSITORIO!
# Si estás en el script principal y el CSV está en 'data/':
data_dir = Path("./data") 

CSV_FILENAME = "DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv"
CSV_PATH = data_dir / CSV_FILENAME
DB_FILE = 'localidades.sqlite'
TABLE_NAME = 'Localidades'

# Nombres de las columnas de localidad según tu dataset:
COLUMNS_MAPPING = {
    'UBIGEO_HECHO': 'UBIGEO',
    'DPTO_HECHO_NEW': 'DEPARTAMENTO',
    'PROV_HECHO': 'PROVINCIA',
    'DIST_HECHO': 'DISTRITO'
}
COLUMNS_TO_EXTRACT = list(COLUMNS_MAPPING.keys())

def generate_localidades_db(csv_path: Path, db_name: str, table_name: str):
    print(f"Buscando archivo en: {csv_path.resolve()}")
    
    # 1. Cargar el Dataset
    try:
        # Usamos 'latin1' o 'ISO-8859-1' que suele ser común para archivos generados en Perú,
        # y 'low_memory=False' para asegurar la carga completa.
        df_denuncias = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
        print(f"Carga exitosa. Filas leídas: {len(df_denuncias)}")
    except FileNotFoundError:
        print(f"🚨 Error: El archivo CSV no fue encontrado en {csv_path.resolve()}. Verifica tu variable 'data_dir'.")
        return
    except Exception as e:
        print(f"🚨 Error al leer el CSV: {e}")
        return

    # 2. Preparar la tabla de localidades
    
    # Verificar si todas las columnas necesarias existen en el DataFrame
    if not all(col in df_denuncias.columns for col in COLUMNS_TO_EXTRACT):
        missing_cols = [col for col in COLUMNS_TO_EXTRACT if col not in df_denuncias.columns]
        print(f"🚨 Error: Faltan las siguientes columnas de localidad en el CSV: {missing_cols}")
        return

    # Seleccionar, renombrar y limpiar
    df_localidades = df_denuncias[COLUMNS_TO_EXTRACT].copy()
    df_localidades.rename(columns=COLUMNS_MAPPING, inplace=True)
    
    # Limpieza: Convertir UBIGEO a string y manejar posibles nulos
    df_localidades['UBIGEO'] = df_localidades['UBIGEO'].astype(str)
    df_localidades.dropna(subset=['UBIGEO'], inplace=True)
    
    # Eliminar duplicados para obtener la lista única de jurisdicciones
    df_localidades.drop_duplicates(subset=['UBIGEO'], inplace=True)
    df_localidades.set_index('UBIGEO', inplace=True)

    # 3. Crear y Conectar a la Base de Datos SQLite
    try:
        conn = sqlite3.connect(db_name)
        
        # 4. Insertar datos en SQLite
        # Esto crea o reemplaza la tabla Localidades con los datos únicos.
        df_localidades.to_sql(table_name, conn, if_exists='replace', index=True)

        # 5. Verificar y cerrar conexión
        count = pd.read_sql(f"SELECT COUNT(*) FROM {table_name}", conn).iloc[0, 0]
        conn.close()

        print(f"\n✅ Base de datos SQLite '{db_name}' creada/actualizada.")
        print(f"Tabla '{table_name}' creada con {count} registros únicos (UBIGEOs).")
        
    except sqlite3.Error as e:
        print(f"🚨 Ocurrió un error de SQLite: {e}")

# Ejecutar la función
# Asegúrate de que tu directorio 'data' exista y contenga el CSV.
generate_localidades_db(CSV_PATH, DB_FILE, TABLE_NAME)
