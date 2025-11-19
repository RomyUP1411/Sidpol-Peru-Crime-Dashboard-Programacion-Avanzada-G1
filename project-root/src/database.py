import sqlite3
import pandas as pd
from pathlib import Path
from utils import log_time, logger
import json
import hashlib
from typing import Tuple, Optional
import processing

# Ruta de la base de datos
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "denuncias.db"


def init_db():
    """Inicializa la conexión y crea el esquema si falta."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    create_schema(conn)
    return conn


def create_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript(
        """
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS fuentes (
        id INTEGER PRIMARY KEY,
        filename TEXT UNIQUE,
        url TEXT,
        downloaded_at TEXT,
        sha256 TEXT,
        size_bytes INTEGER
    );
    CREATE TABLE IF NOT EXISTS departamentos (
        id INTEGER PRIMARY KEY,
        nombre TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS modalidades (
        id INTEGER PRIMARY KEY,
        nombre TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS denuncias (
        id INTEGER PRIMARY KEY,
        anio INTEGER,
        mes INTEGER,
        departamento_id INTEGER,
        provincia TEXT,
        distrito TEXT,
        modalidad_id INTEGER,
        cantidad INTEGER,
        fuente_id INTEGER,
        FOREIGN KEY(departamento_id) REFERENCES departamentos(id),
        FOREIGN KEY(modalidad_id) REFERENCES modalidades(id),
        FOREIGN KEY(fuente_id) REFERENCES fuentes(id)
    );
    """
    )
    conn.commit()


@log_time
def cargar_csv_a_bd(csv_path):
    """Carga datos del CSV a la BD SQLite"""
    try:
        conn = init_db()

        # Intentar leer con utf-8 y fallback a latin1
        try:
            raw = pd.read_csv(csv_path, encoding="utf-8")
        except Exception:
            raw = pd.read_csv(csv_path, encoding="latin1")

        # Utilizar las funciones de procesamiento para estandarizar columnas
        df = processing.clean(raw)

        # Calcular hash y metadatos del archivo
        try:
            with open(csv_path, "rb") as f:
                content = f.read()
            sha256 = hashlib.sha256(content).hexdigest()
            size_bytes = len(content)
        except Exception:
            sha256 = None
            size_bytes = None

        cur = conn.cursor()

        # Crear o recuperar fuente
        filename = Path(csv_path).name
        cur.execute("SELECT id FROM fuentes WHERE filename = ?", (filename,))
        row = cur.fetchone()
        if row:
            fuente_id = row[0]
        else:
            cur.execute(
                "INSERT INTO fuentes (filename, downloaded_at, sha256, size_bytes, url) VALUES (?, datetime('now'), ?, ?, ?)",
                (filename, sha256, size_bytes, None),
            )
            fuente_id = cur.lastrowid

        # Caches para evitar consultas repetidas
        dept_cache = {}
        mod_cache = {}

        def get_or_create_departamento(conn, nombre: str) -> int:
            if nombre in dept_cache:
                return dept_cache[nombre]
            c = conn.cursor()
            c.execute("SELECT id FROM departamentos WHERE nombre = ?", (nombre,))
            r = c.fetchone()
            if r:
                dept_cache[nombre] = r[0]
                return r[0]
            c.execute("INSERT INTO departamentos (nombre) VALUES (?)", (nombre,))
            conn.commit()
            dept_cache[nombre] = c.lastrowid
            return c.lastrowid

        def get_or_create_modalidad(conn, nombre: str) -> int:
            if nombre in mod_cache:
                return mod_cache[nombre]
            c = conn.cursor()
            c.execute("SELECT id FROM modalidades WHERE nombre = ?", (nombre,))
            r = c.fetchone()
            if r:
                mod_cache[nombre] = r[0]
                return r[0]
            c.execute("INSERT INTO modalidades (nombre) VALUES (?)", (nombre,))
            conn.commit()
            mod_cache[nombre] = c.lastrowid
            return c.lastrowid

        # Preparar lista de inserts
        inserts = []
        for _, r in df.iterrows():
            anio = int(r.get("AÑO")) if pd.notna(r.get("AÑO")) else None
            mes = int(r.get("MES")) if pd.notna(r.get("MES")) else None
            dept = r.get("DEPARTAMENTO") if pd.notna(r.get("DEPARTAMENTO")) else None
            prov = r.get("PROVINCIA") if pd.notna(r.get("PROVINCIA")) else None
            dist = r.get("DISTRITO") if pd.notna(r.get("DISTRITO")) else None
            mod = r.get("MODALIDADES") if pd.notna(r.get("MODALIDADES")) else None
            cant = int(r.get("cantidad")) if pd.notna(r.get("cantidad")) else 0

            dept_id = get_or_create_departamento(conn, str(dept)) if dept else None
            mod_id = get_or_create_modalidad(conn, str(mod)) if mod else None

            inserts.append((anio, mes, dept_id, prov, dist, mod_id, cant, fuente_id))

        cur.executemany(
            "INSERT INTO denuncias (anio, mes, departamento_id, provincia, distrito, modalidad_id, cantidad, fuente_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            inserts,
        )
        conn.commit()
        total = cur.rowcount
        conn.close()
        logger.info(f"CSV cargado en BD: {csv_path} ({len(inserts)} filas)")
        return len(inserts), True
    except Exception as e:
        logger.exception(f"Error cargando CSV a BD: {e}")
        return 0, False

def consultar_bd(sql_query):
    """Ejecuta una consulta SQL y retorna DataFrame"""
    try:
        conn = init_db()
        resultado = pd.read_sql_query(sql_query, conn)
        conn.close()
        return resultado, True
    except Exception as e:
        logger.exception(f"Error en consulta SQL: {e}")
        return None, False

def obtener_denuncias_por_modalidad():
    """Consulta: denuncias agrupadas por modalidad"""
    query = """
    SELECT m.nombre as MODALIDADES, SUM(d.cantidad) as total
    FROM denuncias d
    LEFT JOIN modalidades m ON d.modalidad_id = m.id
    GROUP BY m.nombre
    ORDER BY total DESC
    """
    return consultar_bd(query)

def obtener_denuncias_por_departamento():
    """Consulta: top 10 departamentos con más denuncias"""
    query = """
    SELECT dep.nombre as DEPARTAMENTO, SUM(d.cantidad) as total
    FROM denuncias d
    LEFT JOIN departamentos dep ON d.departamento_id = dep.id
    GROUP BY dep.nombre
    ORDER BY total DESC
    LIMIT 10
    """
    return consultar_bd(query)

def obtener_tendencia_mensual(año):
    """Consulta: tendencia de denuncias por mes en un año"""
    query = f"""
    SELECT d.mes as MES, SUM(d.cantidad) as total
    FROM denuncias d
    WHERE d.anio = {año}
    GROUP BY d.mes
    ORDER BY d.mes
    """
    return consultar_bd(query)

def obtener_denuncias_por_provincia(departamento):
    """Consulta: denuncias por provincia dentro de un departamento"""
    query = f"""
    SELECT d.provincia as PROVINCIA, SUM(d.cantidad) as total
    FROM denuncias d
    LEFT JOIN departamentos dep ON d.departamento_id = dep.id
    WHERE dep.nombre = '{departamento}'
    GROUP BY d.provincia
    ORDER BY total DESC
    """
    return consultar_bd(query)

def obtener_estadisticas_generales():
    """Consulta: estadísticas generales de la BD"""
    query = """
    SELECT 
        COUNT(DISTINCT anio) as años,
        COUNT(DISTINCT dep.nombre) as departamentos,
        COUNT(DISTINCT mod.nombre) as modalidades,
        SUM(d.cantidad) as total_denuncias
    FROM denuncias d
    LEFT JOIN departamentos dep ON d.departamento_id = dep.id
    LEFT JOIN modalidades mod ON d.modalidad_id = mod.id
    """
    return consultar_bd(query)

def obtener_tabla_completa(limite=100):
    """Obtiene los primeros N registros de la tabla"""
    query = f"SELECT d.id, d.anio, d.mes, dep.nombre as DEPARTAMENTO, d.provincia, d.distrito, mod.nombre as MODALIDADES, d.cantidad, f.filename as fuente FROM denuncias d LEFT JOIN departamentos dep ON d.departamento_id = dep.id LEFT JOIN modalidades mod ON d.modalidad_id = mod.id LEFT JOIN fuentes f ON d.fuente_id = f.id LIMIT {limite}"
    return consultar_bd(query)


def obtener_denuncias_join(limite=100):
    """Ejemplo de JOIN: devuelve denuncias con nombres de departamento y modalidad."""
    query = f"SELECT d.id, d.anio, d.mes, dep.nombre as departamento, mod.nombre as modalidad, d.cantidad FROM denuncias d LEFT JOIN departamentos dep ON d.departamento_id = dep.id LEFT JOIN modalidades mod ON d.modalidad_id = mod.id ORDER BY d.anio DESC, d.mes DESC LIMIT {limite}"
    return consultar_bd(query)
