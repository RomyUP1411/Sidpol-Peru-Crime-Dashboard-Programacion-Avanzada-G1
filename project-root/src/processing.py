from pathlib import Path
import pandas as pd

def data_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv"

def load_raw(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Tipos según diccionario
    df["ANIO"] = pd.to_numeric(df["ANIO"], errors="coerce").astype("Int64")
    df["MES"]  = pd.to_numeric(df["MES"],  errors="coerce").astype("Int64")
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype("int64")
    # Renombrar columnas para la UI
    df = df.rename(columns={
        "ANIO": "AÑO",
        "DPTO_HECHO_NEW": "DEPARTAMENTO",
        "PROV_HECHO": "PROVINCIA",
        "DIST_HECHO": "DISTRITO",
        "P_MODALIDADES": "MODALIDADES"
    })
    # Casteo de texto con nuevos nombres
    for col in ["DEPARTAMENTO","PROVINCIA","DISTRITO","MODALIDADES"]:
        if col in df.columns:
            df[col] = df[col].astype("string")
    return df.dropna(subset=["AÑO","MES"])

def filter_df(df: pd.DataFrame, anio: int | None, modalidades: list[str] | None,
              dpto: str | None, prov: str | None, mes_range: tuple[int,int] | None) -> pd.DataFrame:
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

def by_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("MODALIDADES", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False)

def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("MES", as_index=False)["cantidad"].sum().sort_values("MES")

def top_departamentos(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("DEPARTAMENTO", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False).head(10)

def heatmap_modalidad_mes(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["MODALIDADES","MES"], as_index=False)["cantidad"].sum()