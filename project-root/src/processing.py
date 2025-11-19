from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


# Devuelve la ruta del CSV en data/; toma el más reciente disponible
def data_path() -> Path:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    candidates = sorted(
        data_dir.glob("DATASET_Denuncias_Policiales*.csv"),
        key=lambda p: p.stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError("No se encontró el CSV en data/. Usa el botón de scraping o coloca el archivo.")
    return candidates[-1]


def load_raw(path: Path) -> pd.DataFrame:
    # Maneja BOM y carga perezosa
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia, renombra y tipifica columnas para la UI."""
    df = _normalize_cols(df)

    rename_candidates = {
        "ANIO": "ANO",
        "AÑO": "ANO",
        "A�'O": "ANO",
        "A���'O": "ANO",
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
    effective_map = {src: dst for src, dst in rename_candidates.items() if src in df.columns}
    df = df.rename(columns=effective_map)

    if "ANO" in df.columns:
        df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype("Int64")
    if "MES" in df.columns:
        df["MES"] = pd.to_numeric(df["MES"], errors="coerce").astype("Int64")
    if "cantidad" in df.columns:
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype("int64")

    for col in ["DEPARTAMENTO", "PROVINCIA", "DISTRITO", "MODALIDADES"]:
        if col in df.columns:
            df[col] = df[col].astype("string")

    if "MES" in df.columns:
        df = df[(df["MES"] >= 1) & (df["MES"] <= 12)]
    if "cantidad" in df.columns:
        df.loc[df["cantidad"] < 0, "cantidad"] = 0

    req = [c for c in ["ANO", "MES"] if c in df.columns]
    if req:
        df = df.dropna(subset=req)

    return df


def filter_df(
    df: pd.DataFrame,
    anio: Optional[int],
    modalidades: Optional[List[str]],
    dpto: Optional[str],
    prov: Optional[str],
    mes_range: Optional[Tuple[int, int]],
) -> pd.DataFrame:
    out = df
    if anio is not None and "ANO" in out.columns:
        out = out[out["ANO"] == anio]
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
    return df.groupby("MES", as_index=False)["cantidad"].sum().sort_values("MES")


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


def compute_kpis(df: pd.DataFrame) -> Dict[str, object]:
    if df.empty or "cantidad" not in df.columns:
        return {"total": 0, "var_pct": 0.0, "top_modalidad": "N/A", "top_departamento": "N/A"}

    total = int(df["cantidad"].sum())

    var_pct = 0.0
    if all(c in df.columns for c in ["ANO", "MES"]):
        series = df.groupby(["ANO", "MES"])["cantidad"].sum().sort_index()
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
