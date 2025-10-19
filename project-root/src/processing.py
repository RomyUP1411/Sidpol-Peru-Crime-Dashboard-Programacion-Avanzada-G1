from pathlib import Path
import pandas as pd

def data_path() -> Path:
    # project-root/src/processing.py -> subir a project-root/data/
    return Path(__file__).resolve().parents[1] / "data" / "DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv"

def load_raw(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ANIO"] = pd.to_numeric(df["ANIO"], errors="coerce").astype("Int64")
    df["MES"] = pd.to_numeric(df["MES"], errors="coerce").astype("Int64")
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype("int64")
    for col in ["DPTO_HECHO_NEW","PROV_HECHO","DIST_HECHO","P_MODALIDADES"]:
        if col in df.columns:
            df[col] = df[col].astype("string")
    return df.dropna(subset=["ANIO","MES"])

def filter_df(df: pd.DataFrame, anio: int, modalidades: list[str] | None, dpto: str | None) -> pd.DataFrame:
    out = df[df["ANIO"] == anio]
    if modalidades:
        out = out[out["P_MODALIDADES"].isin(modalidades)]
    if dpto and dpto != "Todos":
        out = out[out["DPTO_HECHO_NEW"] == dpto]
    return out

def by_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("P_MODALIDADES", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False)

def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    # Serie simple por mes (1-12) sumada para el año seleccionado
    return df.groupby("MES", as_index=False)["cantidad"].sum().sort_values("MES")