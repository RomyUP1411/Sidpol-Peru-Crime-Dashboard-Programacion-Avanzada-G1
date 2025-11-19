from __future__ import annotations

from pathlib import Path
from typing import Tuple, Optional, List, Dict

import pandas as pd


# Devuelve la ruta del CSV en data/; intenta nombre exacto y, si no, busca por patrón
def data_path() -> Path:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    exact = data_dir / "DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv"
    if exact.exists():
        return exact
    # Fallback: primer CSV que empiece con el patrón
    for p in sorted(data_dir.glob("DATASET_Denuncias_Policiales*.csv")):
        return p
    raise FileNotFoundError("No se encontró el CSV en data/; verifica el nombre o ruta.")


# Lee el CSV original (maneja BOM y carga perezosa)
def load_raw(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


# Normaliza nombres de columnas
def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


# Limpia, tipifica y renombra encabezados para la UI
def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = _normalize_cols(df)

    # Soporta variantes con y sin subrayados
    rename_candidates = {
        "ANIO": "AÑO",
        "AÑO": "AÑO",
        "MES": "MES",
        "DPTOHECHONEW": "DEPARTAMENTO",
        "DPTO_HECHO_NEW": "DEPARTAMENTO",
        "PROVHECHO": "PROVINCIA",
        "PROV_HECHO": "PROVINCIA",
        "DISTHECHO": "DISTRITO",
        "DIST_HECHO": "DISTRITO",
        "PMODALIDADES": "MODALIDADES",
        "P_MODALIDADES": "MODALIDADES",
        "cantidad": "cantidad",
        "CANTIDAD": "cantidad",
    }
    # Construir mapa efectivo solo con columnas presentes
    effective_map = {src: dst for src, dst in rename_candidates.items() if src in df.columns}
    df = df.rename(columns=effective_map)

    # Tipificación conforme al diccionario
    if "AÑO" in df.columns:
        df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce").astype("Int64")
    if "MES" in df.columns:
        df["MES"] = pd.to_numeric(df["MES"], errors="coerce").astype("Int64")
    if "cantidad" in df.columns:
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype("int64")

    # Asegurar tipos string para categóricas esperadas
    for col in ["DEPARTAMENTO", "PROVINCIA", "DISTRITO", "MODALIDADES"]:
        if col in df.columns:
            df[col] = df[col].astype("string")

    # Limpiar valores inválidos
    if "MES" in df.columns:
        df = df[(df["MES"] >= 1) & (df["MES"] <= 12)]
    if "cantidad" in df.columns:
        df.loc[df["cantidad"] < 0, "cantidad"] = 0

    # Remover filas sin año/mes válidos
    req = [c for c in ["AÑO", "MES"] if c in df.columns]
    if req:
        df = df.dropna(subset=req)

    return df


# Filtro único para año, modalidades, dpto, provincia, rango de meses
def filter_df(
    df: pd.DataFrame,
    anio: Optional[int],
    modalidades: Optional[List[str]],
    dpto: Optional[str],
    prov: Optional[str],
    mes_range: Optional[Tuple[int, int]],
) -> pd.DataFrame:
    out = df
    if anio is not None and "AÑO" in out.columns:
        out = out[out["AÑO"] == anio]
    if modalidades and "MODALIDADES" in out.columns:
        out = out[out["MODALIDADES"].isin(modalidades)]
    if dpto and dpto != "Todos" and "DEPARTAMENTO" in out.columns:
        out = out[out["DEPARTAMENTO"] == dpto]
    if prov and prov != "Todas" and "PROVINCIA" in out.columns:
        out = out[out["PROVINCIA"] == prov]
    if mes_range and "MES" in out.columns:
        lo, hi = mes_range
        out = out[(out["MES"] >= lo) & (out["MES"] <= hi)]
    return out


# Agregaciones para visualizaciones
def by_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "MODALIDADES" not in df.columns:
        return pd.DataFrame({"MODALIDADES": [], "cantidad": []})
    return (
        df.groupby("MODALIDADES", as_index=False)["cantidad"]
        .sum()
        .sort_values("cantidad", ascending=False)
    )


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "MES" not in df.columns:
        return pd.DataFrame({"MES": [], "cantidad": []})
    return (
        df.groupby("MES", as_index=False)["cantidad"]
        .sum()
        .sort_values("MES")
    )

def data_path() -> Path:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    
    # 1. Prioridad: El archivo estandarizado que descarga nuestro script
    nuevo_estandar = data_dir / "DATASET_Denuncias_Policiales.csv"
    if nuevo_estandar.exists():
        return nuevo_estandar
        
    # 2. Fallback: Busca el nombre antiguo específico (si no se ha actualizado aún)
    antiguo_exacto = data_dir / "DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv"
    if antiguo_exacto.exists():
        return antiguo_exacto

    # 3. Último recurso: Cualquier CSV que empiece con el patrón
    for p in sorted(data_dir.glob("DATASET_Denuncias_Policiales*.csv")):
        return p
        
    raise FileNotFoundError("No se encontró el CSV en data/; verifica haber ejecutado la actualización.")


def top_departamentos(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if df.empty or "DEPARTAMENTO" not in df.columns:
        return pd.DataFrame({"DEPARTAMENTO": [], "cantidad": []})
    return (
        df.groupby("DEPARTAMENTO", as_index=False)["cantidad"]
        .sum()
        .sort_values("cantidad", ascending=False)
        .head(n)
    )


def heatmap_modalidad_mes(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or not {"MODALIDADES", "MES"}.issubset(df.columns):
        return pd.DataFrame({"MODALIDADES": [], "MES": [], "cantidad": []})
    return (
        df.groupby(["MODALIDADES", "MES"], as_index=False)["cantidad"]
        .sum()
        .sort_values(["MODALIDADES", "MES"])
    )


# KPIs calculados sobre el DataFrame filtrado
def compute_kpis(df: pd.DataFrame) -> Dict[str, object]:
    if df.empty or "cantidad" not in df.columns:
        return {"total": 0, "var_pct": 0.0, "top_modalidad": "N/A", "top_departamento": "N/A"}

    total = int(df["cantidad"].sum())

    var_pct = 0.0
    if all(c in df.columns for c in ["AÑO", "MES"]):
        series = df.groupby(["AÑO", "MES"])["cantidad"].sum().sort_index()
        if len(series) >= 2:
            prev = series.iloc[-2]
            curr = series.iloc[-1]
            base = prev if prev != 0 else 1
            var_pct = float((curr - prev) / base * 100.0)

    top_modalidad = "N/A"
    if "MODALIDADES" in df.columns:
        s = df.groupby("MODALIDADES")["cantidad"].sum().sort_values(ascending=False)
        if len(s) > 0:
            top_modalidad = str(s.index[0])

    top_departamento = "N/A"
    if "DEPARTAMENTO" in df.columns:
        s = df.groupby("DEPARTAMENTO")["cantidad"].sum().sort_values(ascending=False)
        if len(s) > 0:
            top_departamento = str(s.index[0])

    return {
        "total": total,
        "var_pct": round(var_pct, 2),
        "top_modalidad": top_modalidad,
        "top_departamento": top_departamento,

    }
