from __future__ import annotations

import streamlit as st
import pandas as pd

from processing import (
    data_path,
    load_raw,
    clean,
    filter_df,
    by_modalidad,
    monthly_trend,
    top_departamentos,
    heatmap_modalidad_mes,
    compute_kpis,
)
from viz import bar_modalidad, line_trend, bar_top_departamentos, heatmap_mod_mes


# Configuración de la página
st.set_page_config(page_title="SIDPOL Perú - Prototipo", layout="wide")

# Carga de datos con caché
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return clean(load_raw(data_path()))


df = load_data()

# Título y fuente/licencia
st.title("Dashboard de denuncias policiales (SIDPOL) - Prototipo")
st.caption(
    "Fuente: SIDPOL/SIDPPOL – MININTER. Variables: AÑO, MES, DEPARTAMENTO, PROVINCIA, DISTRITO, MODALIDADES, cantidad. Licencia ODC-By."
)

# Controles (Año, Modalidades, Departamento, Provincia dependiente, Rango Mes)
years = sorted([int(x) for x in df["AÑO"].dropna().unique()]) if "AÑO" in df.columns else []
mods = sorted([m for m in df["MODALIDADES"].dropna().unique()]) if "MODALIDADES" in df.columns else []
dptos = sorted([d for d in df["DEPARTAMENTO"].dropna().unique()]) if "DEPARTAMENTO" in df.columns else []

c1, c2, c3, c4 = st.columns(4)
with c1:
    year_sel = st.selectbox("Año", options=years, index=len(years) - 1 if years else 0) if years else None
with c2:
    mods_sel = st.multiselect("Modalidades", options=mods, default=mods[:3] if len(mods) >= 3 else mods)
with c3:
    dpto_sel = st.selectbox("Departamento", options=["Todos"] + dptos, index=0) if dptos else "Todos"
with c4:
    mes_sel = st.slider("Mes (rango)", min_value=1, max_value=12, value=(1, 12), step=1)

# Control dependiente de provincia si se eligió un departamento
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
k2.metric(label="Variación % vs período previo", value=f"{kpis['var_pct']}%")
k3.metric(label="Modalidad más frecuente", value=kpis["top_modalidad"])
k4.metric(label="Departamento con más denuncias", value=kpis["top_departamento"])

# Tabla principal
st.subheader("Tabla filtrada")
if df_f.empty:
    st.info("No hay registros para el filtro seleccionado.")
else:
    st.dataframe(
        df_f[["AÑO", "MES", "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "MODALIDADES", "cantidad"]]
        .sort_values(["MES", "cantidad"], ascending=[True, False]),
        use_container_width=True,
    )

# Gráficos
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

# Nota final de citación
st.caption("Datos 2018–2025, cortes mensuales; procedencia y variables según diccionario y metadatos de SIDPOL/SIDPPOL – MININTER.")