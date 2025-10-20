import streamlit as st
import pandas as pd
from processing import (
    data_path, load_raw, clean, filter_df,
    by_modalidad, monthly_trend, top_departamentos, heatmap_modalidad_mes
)
from viz import bar_modalidad, line_trend, bar_top_departamentos, heatmap_mod_mes

# Configuración básica de la página
st.set_page_config(page_title="SIDPOL Perú - Prototipo", layout="wide")

# Carga de datos con caché para agilizar la experiencia
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return clean(load_raw(data_path()))

df = load_data()

# Título y fuente/licencia visibles en la interfaz
st.title("Dashboard de denuncias policiales (SIDPOL) - Prototipo")
st.caption("Fuente: SIDPOL/SIDPPOL – MININTER. Variables: AÑO, MES, DEPARTAMENTO, PROVINCIA, DISTRITO, MODALIDADES, cantidad. Licencia ODC-By.")

# Controles (≥3): año, modalidades, departamento, provincia dependiente, rango de meses
years = sorted([int(x) for x in df["AÑO"].dropna().unique()])
mods = sorted([m for m in df["MODALIDADES"].dropna().unique()])
dptos = sorted([d for d in df["DEPARTAMENTO"].dropna().unique()])

c1, c2, c3, c4 = st.columns(4)
with c1:
    year_sel = st.selectbox("Año", options=years, index=len(years) - 1)
with c2:
    mods_sel = st.multiselect("Modalidades", options=mods, default=mods[:3])
with c3:
    dpto_sel = st.selectbox("Departamento", options=["Todos"] + dptos, index=0)
with c4:
    mes_sel = st.slider("Mes (rango)", min_value=1, max_value=12, value=(1, 12), step=1)

# Control dependiente de provincia si se eligió un departamento
prov_sel = None
if dpto_sel != "Todos":
    provs = sorted([p for p in df[df["DEPARTAMENTO"] == dpto_sel]["PROVINCIA"].dropna().unique()])
    prov_sel = st.selectbox("Provincia", options=["Todas"] + provs, index=0)

# Aplicar filtros
df_f = filter_df(df, year_sel, mods_sel, dpto_sel, prov_sel, mes_sel)

# Indicador simple de total filtrado
st.metric("Total de denuncias (filtro activo)", int(df_f["cantidad"].sum()))

# Tabla principal
st.subheader("Tabla filtrada")
st.dataframe(
    df_f[["AÑO", "MES", "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "MODALIDADES", "cantidad"]]
    .sort_values(["MES", "cantidad"], ascending=[True, False]),
    use_container_width=True
)

# Gráficos (≥3): barras por modalidad, línea mensual, top departamentos (o heatmap alternativo)
col1, col2 = st.columns(2)
with col1:
    st.subheader("Denuncias por modalidad")
    st.altair_chart(bar_modalidad(by_modalidad(df_f)), use_container_width=True)
with col2:
    st.subheader("Tendencia mensual")
    st.altair_chart(line_trend(monthly_trend(df_f)), use_container_width=True)

st.subheader("Top 10 departamentos")
st.altair_chart(bar_top_departamentos(top_departamentos(df_f)), use_container_width=True)

# Alternativa: descomentar para usar heatmap en lugar del top
# st.subheader("Modalidad vs Mes (heatmap)")
# st.altair_chart(heatmap_mod_mes(heatmap_modalidad_mes(df_f)), use_container_width=True)

# Nota final de citación
st.caption("Datos 2018–2025, cortes mensuales; procedencia y variables según diccionario y metadatos de SIDPOL/SIDPPOL – MININTER.")