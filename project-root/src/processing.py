from pathlib import Path
import pandas as pd
from typing import Optional, List
from utils import log_time, logger, handle_errors
from exceptions import ProcessingError, DataLoadError, ValidationError


# Devuelve la ruta absoluta del CSV en la carpeta data/ usando la ubicación de este archivo.
# Si se pasa `filename`, intenta usar ese archivo concreto; si no, devuelve el más
# reciente que comience por "DATASET_Denuncias_Policiales". Si no hay ninguno,
# devuelve el archivo histórico de septiembre si existe, o la ruta esperada para octubre.
def data_path(filename: Optional[str] = None) -> Path:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    if filename:
        candidate = data_dir / filename
        return candidate

    # Buscar archivos que coincidan con el prefijo del dataset
    candidates = list(data_dir.glob("DATASET_Denuncias_Policiales*.csv"))
    if candidates:
        # Devolver el más reciente (por modificación)
        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        logger.debug(f"Archivo de datos más reciente: {latest.name}")
        return latest

    # Nombre histórico presente en el repo (septiembre)
    sept_path = data_dir / "DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv"
    if sept_path.exists():
        logger.debug(f"Usando archivo histórico: {sept_path.name}")
        return sept_path

    # Nombre esperado cuando se descargue la versión más nueva (octubre)
    return data_dir / "DATASET_Denuncias_Policiales_Enero_2018_a_Octubre_2025.csv"


def list_data_files() -> List[Path]:
    """Devuelve la lista de archivos CSV del dataset en `data/`, ordenados por fecha (más reciente primero)."""
    data_dir = Path(__file__).resolve().parents[1] / "data"
    if not data_dir.exists():
        logger.warning("Directorio data/ no existe")
        return []
    candidates = list(data_dir.glob("DATASET_Denuncias_Policiales*.csv"))
    result = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    logger.debug(f"Encontrados {len(result)} archivos de datos")
    return result


@log_time
def load_raw(path: Path) -> pd.DataFrame:
    """Lee el CSV original con los nombres de columnas del recurso oficial"""
    try:
        df = pd.read_csv(path, encoding="utf-8")
        logger.info(f"CSV cargado: {path.name} ({len(df)} filas)")
        return df
    except Exception as e:
        logger.exception(f"Error cargando CSV: {e}")
        raise DataLoadError(f"No se pudo cargar {path}: {e}")


@log_time
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia datos, tipifica columnas y renombra encabezados para mostrarlos legibles en la app"""
    try:
        df = df.copy()
        
        # Tipificación básica conforme al diccionario (año, mes, métrica)
        df["ANIO"] = pd.to_numeric(df["ANIO"], errors="coerce").astype("Int64")
        df["MES"] = pd.to_numeric(df["MES"], errors="coerce").astype("Int64")
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype("int64")
        
        # Renombrado para la UI
        df = df.rename(columns={
            "ANIO": "AÑO",
            "DPTO_HECHO_NEW": "DEPARTAMENTO",
            "PROV_HECHO": "PROVINCIA",
            "DIST_HECHO": "DISTRITO",
            "P_MODALIDADES": "MODALIDADES"
        })
        
        # Asegurar cadenas en columnas categóricas
        for col in ["DEPARTAMENTO", "PROVINCIA", "DISTRITO", "MODALIDADES"]:
            if col in df.columns:
                df[col] = df[col].astype("string")
        
        # Filtrar filas sin año/mes válidos
        initial_rows = len(df)
        df = df.dropna(subset=["AÑO", "MES"])
        final_rows = len(df)
        
        logger.info(f"Clean: {initial_rows} → {final_rows} filas (removidas {initial_rows - final_rows})")
        return df
    except Exception as e:
        logger.exception(f"Error limpiando datos: {e}")
        raise ProcessingError(f"Error en limpieza: {e}")


# Filtro único que aplica año, modalidades, dpto, provincia y rango de meses
def filter_df(
    df: pd.DataFrame,
    anio: int | None,
    modalidades: list[str] | None,
    dpto: str | None,
    prov: str | None,
    mes_range: tuple[int, int] | None
) -> pd.DataFrame:
    """Aplica múltiples filtros al DataFrame"""
    try:
        out = df.copy()
        initial_rows = len(out)
        
        if anio is not None:
            out = out[out["AÑO"] == anio]
            logger.debug(f"Filtro año={anio}: {len(out)} filas")
        
        if modalidades:
            out = out[out["MODALIDADES"].isin(modalidades)]
            logger.debug(f"Filtro modalidades={len(modalidades)}: {len(out)} filas")
        
        if dpto and dpto != "Todos":
            out = out[out["DEPARTAMENTO"] == dpto]
            logger.debug(f"Filtro dpto={dpto}: {len(out)} filas")
        
        if prov and prov != "Todas":
            out = out[out["PROVINCIA"] == prov]
            logger.debug(f"Filtro provincia={prov}: {len(out)} filas")
        
        if mes_range:
            lo, hi = mes_range
            out = out[(out["MES"] >= lo) & (out["MES"] <= hi)]
            logger.debug(f"Filtro meses=[{lo}-{hi}]: {len(out)} filas")
        
        logger.info(f"Filter_df: {initial_rows} → {len(out)} filas aplicadas")
        return out
    except Exception as e:
        logger.exception(f"Error en filter_df: {e}")
        raise ProcessingError(f"Error filtrando datos: {e}")


# Agregación por modalidad para barras
@log_time
def by_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por modalidad y suma cantidad"""
    try:
        if df.empty:
            raise ValidationError("DataFrame vacío para by_modalidad")
        return df.groupby("MODALIDADES", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False)
    except Exception as e:
        logger.exception(f"Error en by_modalidad: {e}")
        raise ProcessingError(f"Error agrupando por modalidad: {e}")


# Serie mensual (1–12) para línea temporal
@log_time
def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por mes y suma cantidad"""
    try:
        if df.empty:
            raise ValidationError("DataFrame vacío para monthly_trend")
        return df.groupby("MES", as_index=False)["cantidad"].sum().sort_values("MES")
    except Exception as e:
        logger.exception(f"Error en monthly_trend: {e}")
        raise ProcessingError(f"Error en tendencia mensual: {e}")


# Top 10 departamentos por total de denuncias
@log_time
def top_departamentos(df: pd.DataFrame) -> pd.DataFrame:
    """Obtiene top 10 departamentos"""
    try:
        if df.empty:
            raise ValidationError("DataFrame vacío para top_departamentos")
        return df.groupby("DEPARTAMENTO", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False).head(10)
    except Exception as e:
        logger.exception(f"Error en top_departamentos: {e}")
        raise ProcessingError(f"Error obteniendo top departamentos: {e}")


# Base para heatmap modalidad x mes
@log_time
def heatmap_modalidad_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por modalidad y mes para heatmap"""
    try:
        if df.empty:
            raise ValidationError("DataFrame vacío para heatmap_modalidad_mes")
        return df.groupby(["MODALIDADES", "MES"], as_index=False)["cantidad"].sum()
    except Exception as e:
        logger.exception(f"Error en heatmap_modalidad_mes: {e}")
        raise ProcessingError(f"Error en heatmap: {e}")