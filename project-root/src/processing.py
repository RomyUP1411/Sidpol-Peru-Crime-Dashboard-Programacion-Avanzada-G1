from pathlib import Path
import pandas as pd
from typing import Optional, List


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
        return latest

    # Nombre histórico presente en el repo (septiembre)
    sept_path = data_dir / "DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv"
    if sept_path.exists():
        return sept_path

    # Nombre esperado cuando se descargue la versión más nueva (octubre)
    return data_dir / "DATASET_Denuncias_Policiales_Enero_2018_a_Octubre_2025.csv"


def list_data_files() -> List[Path]:
    """Devuelve la lista de archivos CSV del dataset en `data/`, ordenados por fecha (más reciente primero)."""
    data_dir = Path(__file__).resolve().parents[1] / "data"
    if not data_dir.exists():
        return []
    candidates = list(data_dir.glob("DATASET_Denuncias_Policiales*.csv"))
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)

# Lee el CSV original con los nombres de columnas del recurso oficial
def load_raw(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")

# Limpia datos, tipifica columnas y renombra encabezados para mostrarlos legibles en la app
def clean(df: pd.DataFrame) -> pd.DataFrame:
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
    return df.dropna(subset=["AÑO", "MES"])

# Filtro único que aplica año, modalidades, dpto, provincia y rango de meses
def filter_df(
    df: pd.DataFrame,
    anio: int | None,
    modalidades: list[str] | None,
    dpto: str | None,
    prov: str | None,
    mes_range: tuple[int, int] | None
) -> pd.DataFrame:
    out = df
    if anio is not None:
        out = out[out["AÑO"] == anio]
    if modalidades:
        out = out[out["MODALIDADES"].isin(modalidades)]
    if dpto and dpto != "Todos":
        out = out[out["DEPARTAMENTO"] == dpto]
    if prov and prov != "Todas":
        out = out[out["PROVINCIA"] == prov]
    if mes_range:
        lo, hi = mes_range
        out = out[(out["MES"] >= lo) & (out["MES"] <= hi)]
    return out

# Agregación por modalidad para barras
def by_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("MODALIDADES", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False)

# Serie mensual (1–12) para línea temporal
def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("MES", as_index=False)["cantidad"].sum().sort_values("MES")

# Top 10 departamentos por total de denuncias
def top_departamentos(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("DEPARTAMENTO", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False).head(10)

# Base para heatmap modalidad x mes
def heatmap_modalidad_mes(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["MODALIDADES", "MES"], as_index=False)["cantidad"].sum()