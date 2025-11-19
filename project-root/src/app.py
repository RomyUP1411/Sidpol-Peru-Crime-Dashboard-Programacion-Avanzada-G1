import streamlit as st
import pandas as pd
from processing import (
    data_path, list_data_files, load_raw, clean, filter_df,
    by_modalidad, monthly_trend, top_departamentos, heatmap_modalidad_mes
)
from viz import bar_modalidad, line_trend, bar_top_departamentos, heatmap_mod_mes
from download_data import download_csv
from database import (
    cargar_csv_a_bd, 
    consultar_bd, 
    obtener_denuncias_por_modalidad,
    obtener_denuncias_por_departamento,
    obtener_tabla_completa,
    obtener_estadisticas_generales,
    obtener_denuncias_join,
)

# Configuración básica de la página
st.set_page_config(page_title="SIDPOL Perú - Prototipo", layout="wide")

# --- Login simple: guardar nombre temporalmente en sesión ---
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "X"

with st.sidebar.expander("Usuario / Login", expanded=False):
    name_input = st.text_input("Nombre", value=st.session_state.get("user_name", "X"))
    if st.button("Iniciar sesión", key="login_btn"):
        st.session_state["user_name"] = name_input.strip() if name_input.strip() else "X"
        st.success(f"Sesión iniciada como {st.session_state['user_name']}")

# Mostrar usuario en la app
st.caption(f"Usuario actual: `{st.session_state.get('user_name', 'X')}`")


# ====== SECCIÓN DE DESCARGA CSV ======
st.title("Dashboard de denuncias policiales (SIDPOL) - Prototipo")
st.caption("Fuente: SIDPOL/SIDPPOL – MININTER. Variables: AÑO, MES, DEPARTAMENTO, PROVINCIA, DISTRITO, MODALIDADES, cantidad. Licencia ODC-By.")

if st.button("📥 Descargar/Actualizar CSV desde datosabiertos.gob.pe"):
    try:
        output_path = download_csv()
        st.success(f"Descarga completada: {output_path.name}")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Ocurrió un error durante la descarga: {e}")
else:
    st.info("Haz clic en el botón para obtener el CSV actualizado desde la fuente oficial.")


# ====== SECCIÓN DE BASE DE DATOS ======
st.divider()
st.subheader("⚙️ Gestión de Base de Datos")

col_db1, col_db2, col_db3 = st.columns(3)

with col_db1:
    if st.button("💾 Cargar CSV a Base de Datos"):
        try:
            csv_to_load = data_path()
            filas, exito = cargar_csv_a_bd(str(csv_to_load))
            if exito:
                st.success(f"✓ {filas} registros cargados a la BD SQLite")
            else:
                st.error("Error al cargar los datos")
        except FileNotFoundError:
            st.error("Descarga primero el CSV con el botón de arriba")
        except Exception as e:
            st.error(f"Error: {e}")

with col_db2:
    if st.button("📊 Estadísticas de BD"):
        try:
            stats, exito = obtener_estadisticas_generales()
            if exito and not stats.empty:
                row = stats.iloc[0]
                st.metric("Años en BD", int(row['años']))
                st.metric("Departamentos", int(row['departamentos']))
                st.metric("Total Denuncias", int(row['total_denuncias']))
            else:
                st.warning("Carga datos a la BD primero")
        except Exception as e:
            st.error(f"Error: {e}")

with col_db3:
    if st.button("🔄 Actualizar desde BD"):
        st.cache_data.clear()
        st.rerun()

st.divider()


# ====== SECCIÓN DE CONSULTAS SQL ======
st.subheader("🔍 Editor de Consultas SQL")

tab_consultas, tab_tabla = st.tabs(["Consulta personalizada", "Ver tabla"])

with tab_consultas:
    col_sql1, col_sql2 = st.columns([3, 1])
    
    with col_sql1:
        sql_query = st.text_area(
            "Escribe tu consulta SQL:",
            value="SELECT * FROM denuncias LIMIT 10",
            height=150
        )
    
    with col_sql2:
        ejecutar_sql = st.button("▶️ Ejecutar", use_container_width=True)
    
    if ejecutar_sql:
        try:
            resultado, exito = consultar_bd(sql_query)
            if exito and resultado is not None:
                st.dataframe(resultado, use_container_width=True)
                st.caption(f"Filas: {len(resultado)}")
            else:
                st.error("Error en la consulta SQL")
        except Exception as e:
            st.error(f"Error SQL: {e}")

    if st.button("🔗 Mostrar ejemplo JOIN (denuncias con departamento y modalidad)"):
        try:
            jtab, ok = obtener_denuncias_join(limite=200)
            if ok and jtab is not None:
                st.dataframe(jtab, use_container_width=True)
            else:
                st.warning("No hay datos o carga la BD primero")
        except Exception as e:
            st.error(f"Error mostrando JOIN: {e}")

with tab_tabla:
    if st.button("Cargar tabla completa desde BD"):
        try:
            tabla, exito = obtener_tabla_completa(limite=500)
            if exito and tabla is not None:
                st.dataframe(tabla, use_container_width=True)
                st.caption(f"Total de filas mostradas: {len(tabla)}")
            else:
                st.warning("Carga datos a la BD primero")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()


# ====== RESTO DE LA APP (CÓDIGO ORIGINAL) ======
# Carga de datos parametrizada (caché por ruta)
@st.cache_data(show_spinner=False)
def load_data(path_str: str) -> pd.DataFrame:
    from pathlib import Path
    return clean(load_raw(Path(path_str)))


# Selector de archivo de datos: permite elegir el más reciente o un CSV concreto
available = list_data_files()
options = ["Último"] + [p.name for p in available]
choice = st.selectbox("Archivo de datos a usar", options=options, index=0)

selected_filename = None if choice == "Último" else choice
dp = data_path(selected_filename)

# Mostrar info del archivo seleccionado
try:
    if dp.exists():
        mtime = dp.stat().st_mtime
        import datetime
        ts = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Archivo de datos seleccionado: `{dp.name}` — modificado: {ts}")
    else:
        st.caption(f"Archivo de datos seleccionado: `{dp.name}` (no existe aún)")
except Exception:
    pass

# KPIs desde la base de datos (si hay datos)
try:
    stats_df, ok = obtener_estadisticas_generales()
    if ok and stats_df is not None and not stats_df.empty:
        row = stats_df.iloc[0]
        k1, k2, k3 = st.columns(3)
        k1.metric("Años en BD", int(row["años"]))
        k2.metric("Departamentos", int(row["departamentos"]))
        k3.metric("Total denuncias (BD)", int(row["total_denuncias"]))
except Exception:
    pass

# Cargar DataFrame usando la ruta seleccionada
try:
    df = load_data(str(dp))
except FileNotFoundError:
    st.error("Archivo seleccionado no encontrado. Descarga el CSV o elige otro archivo.")
    st.stop()
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()


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
