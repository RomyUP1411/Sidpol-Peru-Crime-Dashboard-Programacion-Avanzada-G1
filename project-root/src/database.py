import sqlite3
import pandas as pd
from pathlib import Path
from utils import log_time, logger

# Ruta de la base de datos
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "denuncias.db"

def init_db():
    """Inicializa la conexión a la base de datos"""
    conn = sqlite3.connect(str(DB_PATH))
    return conn

@log_time
def cargar_csv_a_bd(csv_path):
    """Carga datos del CSV a la BD SQLite"""
    try:
        conn = init_db()
        df = pd.read_csv(csv_path, encoding='utf-8')
        # Si la tabla ya existe, la reemplaza
        df.to_sql('denuncias', conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()
        logger.info(f"CSV cargado en BD: {csv_path} ({len(df)} filas)")
        return len(df), True
    except Exception as e:
        logger.exception(f"Error cargando CSV a BD: {e}")
        return 0, False

def consultar_bd(sql_query):
    """Ejecuta una consulta SQL y retorna DataFrame"""
    try:
        conn = init_db()
        resultado = pd.read_sql(sql_query, conn)
        conn.close()
        return resultado, True
    except Exception as e:
        return None, False

def obtener_denuncias_por_modalidad():
    """Consulta: denuncias agrupadas por modalidad"""
    query = """
    SELECT MODALIDADES, SUM(cantidad) as total
    FROM denuncias
    GROUP BY MODALIDADES
    ORDER BY total DESC
    """
    return consultar_bd(query)

def obtener_denuncias_por_departamento():
    """Consulta: top 10 departamentos con más denuncias"""
    query = """
    SELECT DEPARTAMENTO, SUM(cantidad) as total
    FROM denuncias
    GROUP BY DEPARTAMENTO
    ORDER BY total DESC
    LIMIT 10
    """
    return consultar_bd(query)

def obtener_tendencia_mensual(año):
    """Consulta: tendencia de denuncias por mes en un año"""
    query = f"""
    SELECT MES, SUM(cantidad) as total
    FROM denuncias
    WHERE AÑO = {año}
    GROUP BY MES
    ORDER BY MES
    """
    return consultar_bd(query)

def obtener_denuncias_por_provincia(departamento):
    """Consulta: denuncias por provincia dentro de un departamento"""
    query = f"""
    SELECT PROVINCIA, SUM(cantidad) as total
    FROM denuncias
    WHERE DEPARTAMENTO = '{departamento}'
    GROUP BY PROVINCIA
    ORDER BY total DESC
    """
    return consultar_bd(query)

def obtener_estadisticas_generales():
    """Consulta: estadísticas generales de la BD"""
    query = """
    SELECT 
        COUNT(DISTINCT AÑO) as años,
        COUNT(DISTINCT DEPARTAMENTO) as departamentos,
        COUNT(DISTINCT MODALIDADES) as modalidades,
        SUM(cantidad) as total_denuncias
    FROM denuncias
    """
    return consultar_bd(query)

def obtener_tabla_completa(limite=100):
    """Obtiene los primeros N registros de la tabla"""
    query = f"SELECT * FROM denuncias LIMIT {limite}"
    return consultar_bd(query)