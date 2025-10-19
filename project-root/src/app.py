import streamlit as st
from pathlib import Path
import pandas as pd
from processing import data_path, load_raw, clean, filter_df, by_modalidad, monthly_trend
from viz import bar_modalidad, line_trend

st.set_page_config(page_title="SIDPOL Perú - Prototipo", layout="wide")

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return clean(load_raw(data_path()))

df = load_data()

st.title("Dashboard de denuncias policiales (SIDPOL) - Prototipo")
st.caption("Fuente: SIDPOL/SIDPPOL – MININTER. Variables: ANIO, MES, DPTO/PROV/DIST, UBIGEO, P_MODALIDADES, cantidad. Licencia ODC-By.")

# Controles
years = sorted([int(x) for x in df["ANIO"].dropna().unique()])
mods = sorted([m for m in df["P_MODALIDADES"].dropna().unique()])
dptos = sorted([d for d in df["DPTO_HECHO_NEW"].dropna().unique()])

c1, c2, c3 = st.columns(3)
with c1: year_sel = st.selectbox("Año", options=years, index=len(years)-1)
with c2: mods_sel = st.multiselect("Modalidades", options=mods, default=mods[:3])
with c3: dpto_sel = st.selectbox("Departamento", options=["Todos"] + dptos, index=0)

# Datos filtrados
df_f = filter_df(df, year_sel, mods_sel, dpto_sel)

# Tabla
st.subheader("Tabla filtrada")
st.dataframe(
    df_f[["ANIO","MES","DPTO_HECHO_NEW","PROV_HECHO","DIST_HECHO","P_MODALIDADES","cantidad"]]
    .sort_values(["MES","cantidad"], ascending=[True, False]),
    use_container_width=True
)

# Gráficos
left, right = st.columns(2)
with left:
    st.subheader("Por modalidad")
    st.altair_chart(bar_modalidad(by_modalidad(df_f)), use_container_width=True)
with right:
    st.subheader("Tendencia mensual")
    st.altair_chart(line_trend(monthly_trend(df_f)), use_container_width=True)