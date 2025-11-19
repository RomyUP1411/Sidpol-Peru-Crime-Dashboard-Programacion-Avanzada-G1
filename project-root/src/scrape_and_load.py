from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Desactivar warnings SSL (el portal a veces presenta certificados problemáticos)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuración
URL_RESOURCE = "https://www.datosabiertos.gob.pe/dataset/denuncias-policiales/resource/64c01d53-4402-4e5a-936a-4bce5b3d1008"
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "denuncias.db"
FALLBACK_CSV = "DATASET_Denuncias_Policiales.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


def _slug(text: str) -> str:
    return re.sub(r"\W+", "_", text.strip(), flags=re.UNICODE).strip("_").lower() or "na"


def _find_download_url(session: requests.Session) -> str:
    """Localiza el enlace de descarga del recurso (usa el anchor hacia /node/21805/download)."""
    resp = session.get(URL_RESOURCE, headers=HEADERS, timeout=30, verify=False)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    tag = soup.find("a", href=lambda h: h and "/node/21805/download" in h)
    if not tag or not tag.get("href"):
        raise RuntimeError("No se encontró el enlace de descarga en la página del recurso")
    return urljoin(URL_RESOURCE, tag["href"])


def _filename_from_cd(resp: requests.Response) -> str:
    cd = resp.headers.get("content-disposition", "")
    if "filename=" in cd:
        return cd.split("filename=")[-1].strip('";\' ')
    return FALLBACK_CSV


def download_csv() -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    with requests.Session() as s:
        url = _find_download_url(s)
        print(f"Descargando CSV desde: {url}")
        with s.get(url, headers=HEADERS, stream=True, timeout=120, verify=False) as r:
            r.raise_for_status()
            fname = _filename_from_cd(r) or FALLBACK_CSV
            dst = DATA_DIR / fname
            with open(dst, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    print(f"Archivo guardado en: {dst}")
    return dst


def _clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    rename = {
        "ANIO": "ANO",
        "AÑO": "ANO",
        "A�'O": "ANO",
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
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if "ANO" in df.columns:
        df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype("Int64")
    if "MES" in df.columns:
        df["MES"] = pd.to_numeric(df["MES"], errors="coerce").astype("Int64")
    if "cantidad" in df.columns:
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype("int64")
    return df


def load_to_db(csv_path: Path):
    df = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
    df = _clean_cols(df)

    con = sqlite3.connect(DB_PATH)
    df.to_sql("denuncias", con, if_exists="replace", index=False)

    # Tablas por año
    if "ANO" in df.columns:
        for year in df["ANO"].dropna().unique():
            sub = df[df["ANO"] == year]
            sub.to_sql(f"denuncias_ano_{int(year)}", con, if_exists="replace", index=False)

    # Tablas por departamento
    if "DEPARTAMENTO" in df.columns:
        for dpto in df["DEPARTAMENTO"].dropna().unique():
            sub = df[df["DEPARTAMENTO"] == dpto]
            sub.to_sql(f"denuncias_dpto_{_slug(str(dpto))}", con, if_exists="replace", index=False)

    # Tablas por provincia
    if "PROVINCIA" in df.columns:
        for prov in df["PROVINCIA"].dropna().unique():
            sub = df[df["PROVINCIA"] == prov]
            sub.to_sql(f"denuncias_prov_{_slug(str(prov))}", con, if_exists="replace", index=False)

    con.close()
    print(f"Base SQLite generada en: {DB_PATH}")


def main():
    csv_path = download_csv()
    load_to_db(csv_path)


if __name__ == "__main__":
    main()
