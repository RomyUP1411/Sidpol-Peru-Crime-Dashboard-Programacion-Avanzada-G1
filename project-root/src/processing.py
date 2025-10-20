from pathlib import Path
import pandas as pd

def data_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv"  # mismo nombre que tu archivo [file:23]

def load_raw(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")  # CSV con columnas ANIO, MES, ... según diccionario [file:23][file:24]

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ANIO"] = pd.to_numeric(df["ANIO"], errors="coerce").astype("Int64")  # tipificado según diccionario [file:24]
    df["MES"] = pd.to_numeric(df["MES"], errors="coerce").astype("Int64")    # tipificado según diccionario [file:24]
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype("int64")  # métrica base [file:24]
    for col in ["DPTO_HECHO_NEW","PROV_HECHO","DIST_HECHO","P_MODALIDADES"]:
        if col in df.columns:
            df[col] = df[col].astype("string")  # categorías de texto del dataset [file:24]
    # RENOMBRAR columna visible
    df = df.rename(columns={"ANIO": "AÑO"})  # cambia solo el nombre para la interfaz [file:24]
    return df.dropna(subset=["AÑO","MES"])  # ahora la llave temporal usa AÑO [file:24]

def filter_df(df: pd.DataFrame, anio: int | None, modalidades: list[str] | None,
              dpto: str | None, prov: str | None, mes_range: tuple[int,int] | None) -> pd.DataFrame:
    out = df
    if anio is not None:
        out = out[out["AÑO"] == anio]  # usa el nuevo nombre AÑO [file:24]
    if modalidades:
        out = out[out["P_MODALIDADES"].isin(modalidades)]  # filtro por modalidades del diccionario [file:24]
    if dpto and dpto != "Todos":
        out = out[out["DPTO_HECHO_NEW"] == dpto]  # filtro por departamento conforme a columnas del CSV [file:23]
    if prov and prov != "Todas":
        out = out[out["PROV_HECHO"] == prov]  # filtro por provincia existente en el CSV [file:23]
    if mes_range:
        lo, hi = mes_range
        out = out[(out["MES"] >= lo) & (out["MES"] <= hi)]  # rango de meses 1–12 según CSV [file:23]
    return out

def by_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("P_MODALIDADES", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False)  # agregación por modalidad [file:24]

def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("MES", as_index=False)["cantidad"].sum().sort_values("MES")  # serie mensual 1–12 [file:23]

def top_departamentos(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("DPTO_HECHO_NEW", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False).head(10)  # top 10 deptos [file:23]

def heatmap_modalidad_mes(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["P_MODALIDADES","MES"], as_index=False)["cantidad"].sum()  # base para heatmap modalidad x mes [file:23][file:24]