import sqlite3
import pandas as pd

DATABASE_FILE = 'denuncias_policiales.db'

def get_connection():
    """Conecta con la base de datos SQLite."""
    # Habilita la Clave Foránea (necesario en SQLite para forzar la integridad)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def setup_database(conn):
    """Crea las tablas Ubicaciones y Denuncias_Agregadas."""
    cursor = conn.cursor()
    
    # 1. TABLA UBICACIONES (Padre) - Almacena la jerarquía geográfica
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ubicaciones (
            id_ubicacion INTEGER PRIMARY KEY,
            departamento TEXT NOT NULL,
            provincia TEXT NOT NULL,
            distrito TEXT NOT NULL,
            -- Asumimos que no necesitamos lat/lon en este nivel para simplificar,
            -- pero se agregaría si fuese necesario (e.g., geocodificación posterior).
            UNIQUE (departamento, provincia, distrito) 
        );
    """)
    
    # 2. TABLA DENUNCIAS_AGREGADAS (Hijo) - Almacena los conteos de delitos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Denuncias_Agregadas (
            id_registro INTEGER PRIMARY KEY,
            anio INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            tipo_delito TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            -- Clave foránea que apunta a la ubicación del hecho
            id_ubicacion INTEGER,
            
            FOREIGN KEY(id_ubicacion) REFERENCES Ubicaciones(id_ubicacion)
        );
    """)
    conn.commit()

def insert_ubicacion_and_get_id(conn, depto, prov, dist):
    """
    Busca una ubicación; si no existe, la inserta y devuelve su id_ubicacion.
    """
    cursor = conn.cursor()
    
    # 1. Intenta obtener el ID
    cursor.execute("""
        SELECT id_ubicacion FROM Ubicaciones 
        WHERE departamento = ? AND provincia = ? AND distrito = ?
    """, (depto, prov, dist))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        # 2. Si no existe, insértala y devuelve el nuevo ID
        cursor.execute(
            "INSERT INTO Ubicaciones (departamento, provincia, distrito) VALUES (?, ?, ?)",
            (depto, prov, dist)
        )
        conn.commit()
        return cursor.lastrowid

def insert_denuncias_agregadas(conn, registros):
    """Inserta una lista de registros agregados en la tabla Denuncias_Agregadas."""
    cursor = conn.cursor()
    # Las columnas son: anio, mes, tipo_delito, cantidad, id_ubicacion
    sql = 'INSERT INTO Denuncias_Agregadas (anio, mes, tipo_delito, cantidad, id_ubicacion) VALUES (?, ?, ?, ?, ?)'
    cursor.executemany(sql, registros)
    conn.commit()

def fetch_denuncias_for_dashboard(conn):
    """Consulta con JOIN para obtener todos los datos para el dashboard."""
    query = """
        SELECT
            T1.anio,
            T1.mes,
            T1.tipo_delito,
            T1.cantidad,
            T2.departamento,
            T2.provincia,
            T2.distrito
        FROM
            Denuncias_Agregadas AS T1
        INNER JOIN
            Ubicaciones AS T2 ON T1.id_ubicacion = T2.id_ubicacion;
    """
    df = pd.read_sql_query(query, conn)
    return df