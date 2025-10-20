import streamlit as st
import pandas as pd
from processing import load_raw, clean, data_path, filter_df, by_modalidad, monthly_trend, top_departamentos, heatmap_modalidad_mes
from viz import bar_modalidad, line_trend, bar_top_departamentos, heatmap_mod_mes

st.set_page_config(page_title="SIDPOL Perú - Prototipo", layout="wide")

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return clean(load_raw(data_path()))  # usa procesamiento centralizado conforme a la guía [file:2]

df = load_data()

st.title("Dashboard de denuncias policiales (SIDPOL) - Prototipo")
st.caption("Fuente: SIDPOL/SIDPPOL – MININTER. Variables: AÑO, MES, DPTO/PROV/DIST, UBIGEO, P_MODALIDADES, cantidad. Licencia ODC-By.")  # citación para el parcial [file:2][file:24]

# CONTROLES (≥3)
years = sorted([int(x) for x in df["AÑO"].dropna().unique()])  # ahora usa AÑO [file:24]
mods = sorted([m for m in df["P_MODALIDADES"].dropna().unique()])  # modalidades del diccionario [file:24]
dptos = sorted([d for d in df["DPTO_HECHO_NEW"].dropna().unique()])  # departamentos del CSV [file:23]

c1, c2, c3, c4 = st.columns(4)
with c1:
    year_sel = st.selectbox("Año", options=years, index=len(years)-1)  # Control 1 [file:2]
with c2:
    mods_sel = st.multiselect("Modalidades", options=mods, default=mods[:3])  # Control 2 [file:2]
with c3:
    dpto_sel = st.selectbox("Departamento", options=["Todos"] + dptos, index=0)  # Control 3 [file:2]
with c4:
    # Control 4 opcional: rango de meses 1–12
    mes_sel = st.slider("Mes (rango)", min_value=1, max_value=12, value=(1,12), step=1)  # usa MES 1–12 del CSV [file:23]

# Provincia dependiente (si eliges dpto)
prov_sel = None
if dpto_sel != "Todos":
    provs = sorted([p for p in df[df["DPTO_HECHO_NEW"] == dpto_sel]["PROV_HECHO"].dropna().unique()])
    prov_sel = st.selectbox("Provincia", options=["Todas"] + provs, index=0)  # Control adicional dependiente [file:23]

# FILTROS
df_f = filter_df(df, year_sel, mods_sel, dpto_sel, prov_sel, mes_sel)  # aplica todos los controles [file:2][file:23]

# TABLA
st.subheader("Tabla filtrada")
st.dataframe(
    df_f[["AÑO","MES","DPTO_HECHO_NEW","PROV_HECHO","DIST_HECHO","P_MODALIDADES","cantidad"]]
    .sort_values(["MES","cantidad"], ascending=[True, False]),
    use_container_width=True
)  # visualización en tabla exigida en el parcial [file:2]

# GRÁFICOS (≥3)
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.subheader("Por modalidad")
    st.altair_chart(bar_modalidad(by_modalidad(df_f)), use_container_width=True)  # Gráfico 1 [file:2]
with row1_col2:
    st.subheader("Tendencia mensual")
    st.altair_chart(line_trend(monthly_trend(df_f)), use_container_width=True)  # Gráfico 2 [file:2]

row2_col = st.container()
with row2_col:
    st.subheader("Top 10 departamentos")
    st.altair_chart(bar_top_departamentos(top_departamentos(df_f)), use_container_width=True)  # Gráfico 3 (alternativa: heatmap_mod_mes) [file:2]