from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from processing import (
    clean,
    data_path,
    filter_df,
    load_raw,
    compute_kpis,
    by_modalidad,
    monthly_trend,
    top_departamentos,
)
from viz import bar_modalidad, bar_top_departamentos, line_trend

# Configuracion de la pagina
st.set_page_config(page_title="SIDPOL Peru - Prototipo", layout="wide")


# Carga de datos con cache
@st.cache_data(show_spinner=False)
def load_data(csv_path: Path) -> pd.DataFrame:
    """Carga y limpia el CSV local indicado en data/."""
    return clean(load_raw(csv_path))


# --- CSV local requerido ---
try:
    csv_path = data_path()
except FileNotFoundError as err:
    st.error(f"No se encontró el CSV en data/: {err}")
    st.stop()

df = load_data(csv_path)

with st.sidebar:
    st.header("Datos cargados")
    st.write("Se utiliza el archivo local con denuncias de enero a diciembre 2018.")
    st.code(csv_path.name)
    st.metric("Registros disponibles", f"{len(df):,}")
    st.caption("Para actualizar, reemplaza el CSV en data/ y recarga la app.")

# Titulo y fuente/licencia
st.title("Dashboard de denuncias policiales (SIDPOL) - Prototipo")
st.caption(
    "Fuente: SIDPOL/SIDPPOL - MININTER. Variables: ANO, MES, DEPARTAMENTO, PROVINCIA, DISTRITO, MODALIDADES, cantidad. Licencia ODC-By."
)

# Controles (Ano, Modalidades, Departamento, Provincia dependiente, Rango Mes)
years = sorted([int(x) for x in df["ANO"].dropna().unique()]) if "ANO" in df.columns else []
mods = sorted([m for m in df["MODALIDADES"].dropna().unique()]) if "MODALIDADES" in df.columns else []
dptos = sorted([d for d in df["DEPARTAMENTO"].dropna().unique()]) if "DEPARTAMENTO" in df.columns else []

c1, c2, c3, c4 = st.columns(4)
with c1:
    year_sel = st.selectbox("Ano", options=years, index=len(years) - 1 if years else 0) if years else None
with c2:
    mods_sel = st.multiselect("Modalidades", options=mods, default=mods[:3] if len(mods) >= 3 else mods)
with c3:
    dpto_sel = st.selectbox("Departamento", options=["Todos"] + dptos, index=0) if dptos else "Todos"
with c4:
    mes_sel = st.slider("Mes (rango)", min_value=1, max_value=12, value=(1, 12), step=1)

# Control dependiente de provincia si se eligio un departamento
prov_sel = None
if dpto_sel != "Todos" and "DEPARTAMENTO" in df.columns:
    provs = sorted([p for p in df[df["DEPARTAMENTO"] == dpto_sel]["PROVINCIA"].dropna().unique()]) if "PROVINCIA" in df.columns else []
    prov_sel = st.selectbox("Provincia", options=["Todas"] + provs, index=0) if provs else "Todas"

# Aplicar filtros
df_f = filter_df(df, year_sel, mods_sel, dpto_sel, prov_sel, mes_sel)

# KPIs (fila superior) sobre el filtro activo
kpis = compute_kpis(df_f)
k1, k2, k3, k4 = st.columns(4)
k1.metric(label="Denuncias totales", value=f"{kpis['total']:,}")
k2.metric(label="Variacion % vs periodo previo", value=f"{kpis['var_pct']}%")
k3.metric(label="Modalidad mas frecuente", value=kpis["top_modalidad"])
k4.metric(label="Departamento con mas denuncias", value=kpis["top_departamento"])

# Tabla principal (seleccion segura de columnas)
st.subheader("Tabla filtrada")
display_cols = [c for c in ["ANO", "MES", "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "MODALIDADES", "cantidad"] if c in df_f.columns]
if df_f.empty or not display_cols:
    st.info("No hay registros o columnas esperadas para el filtro seleccionado.")
else:
    st.dataframe(
        df_f[display_cols].sort_values(["MES", "cantidad"], ascending=[True, False]),
        use_container_width=True,
    )

# Graficos
col1, col2 = st.columns(2)
with col1:
    st.subheader("Denuncias por modalidad")
    st.altair_chart(bar_modalidad(by_modalidad(df_f)), use_container_width=True)

with col2:
    st.subheader("Tendencia mensual")
    st.altair_chart(line_trend(monthly_trend(df_f)), use_container_width=True)

st.subheader("Top 10 departamentos")
st.altair_chart(bar_top_departamentos(top_departamentos(df_f)), use_container_width=True)

# Alternativa: heatmap en vez de top
# st.subheader("Modalidad vs Mes (heatmap)")
# st.altair_chart(heatmap_mod_mes(heatmap_modalidad_mes(df_f)), use_container_width=True)

st.caption("Datos enero-diciembre 2018; procedencia y variables segun diccionario y metadatos de SIDPOL/SIDPPOL - MININTER.")
