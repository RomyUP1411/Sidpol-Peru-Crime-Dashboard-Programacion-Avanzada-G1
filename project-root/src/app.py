import streamlit as st
import pandas as pd
import numpy as np
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
    obtener_top_modalidades_por_departamento,
)
from analysis import (
    predict_monthly_trend,
    calculate_growth_rate,
    top_modalidad_by_departamento,
    calculate_correlation_matrix
)
from utils import logger

# Configuración básica de la página
st.set_page_config(page_title="SIDPOL Perú - Prototipo", layout="wide")

logger.info("=== Aplicación Streamlit iniciada ===")

# --- Login simple: guardar nombre temporalmente en sesión ---
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "X"

with st.sidebar.expander("👤 Usuario / Login", expanded=False):
    name_input = st.text_input("Nombre", value=st.session_state.get("user_name", "X"))
    if st.button("Iniciar sesión", key="login_btn"):
        st.session_state["user_name"] = name_input.strip() if name_input.strip() else "X"
        st.success(f"Sesión iniciada como {st.session_state['user_name']}")
        logger.info(f"Usuario {st.session_state['user_name']} inició sesión")

# Mostrar usuario en la app
st.caption(f"👤 Usuario actual: `{st.session_state.get('user_name', 'X')}`")


# ====== SECCIÓN DE DESCARGA CSV ======
st.title("🚔 Dashboard de denuncias policiales (SIDPOL) - Prototipo")
st.caption("Fuente: SIDPOL/SIDPPOL – MININTER. Variables: AÑO, MES, DEPARTAMENTO, PROVINCIA, DISTRITO, MODALIDADES, cantidad. Licencia ODC-By.")

if st.button("📥 Descargar/Actualizar CSV desde datosabiertos.gob.pe"):
    with st.spinner("Descargando datos..."):
        try:
            output_path = download_csv()
            st.success(f"✓ Descarga completada: {output_path.name}")
            logger.info(f"CSV descargado: {output_path.name}")
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error durante descarga: {e}")
            logger.exception(f"Error descargando CSV: {e}")
else:
    st.info("ℹ️ Haz clic en el botón para obtener el CSV actualizado desde la fuente oficial.")


# ====== SECCIÓN DE BASE DE DATOS ======
st.divider()
st.subheader("⚙️ Gestión de Base de Datos")

col_db1, col_db2, col_db3 = st.columns(3)

with col_db1:
    if st.button("💾 Cargar CSV a Base de Datos"):
        with st.spinner("Cargando a BD..."):
            try:
                csv_to_load = data_path()
                filas, exito = cargar_csv_a_bd(str(csv_to_load))
                if exito:
                    st.success(f"✓ {filas} registros cargados a BD SQLite")
                    logger.info(f"Datos cargados a BD: {filas} registros")
                else:
                    st.error("❌ Error al cargar los datos")
                    logger.error("Error cargando datos a BD")
            except FileNotFoundError:
                st.error("❌ Descarga primero el CSV con el botón de arriba")
                logger.error("Archivo CSV no encontrado")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.exception(f"Error: {e}")

with col_db2:
    if st.button("📊 Estadísticas de BD"):
        try:
            stats, exito = obtener_estadisticas_generales()
            if exito and stats is not None and not stats.empty:
                row = stats.iloc[0]
                st.metric("Años en BD", int(row['años']))
                st.metric("Departamentos", int(row['departamentos']))
                st.metric("Modalidades", int(row['modalidades']))
                st.metric("Total Denuncias", int(row['total_denuncias']))
            else:
                st.warning("⚠️ Carga datos a la BD primero")
        except Exception as e:
            st.error(f"❌ Error: {e}")
            logger.exception(f"Error obteniendo estadísticas: {e}")

with col_db3:
    if st.button("🔄 Actualizar caché"):
        st.cache_data.clear()
        st.success("✓ Caché limpiado")
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
                st.caption(f"✓ Filas: {len(resultado)}")
            else:
                st.error("❌ Error en la consulta SQL")
        except Exception as e:
            st.error(f"❌ Error SQL: {e}")
            logger.exception(f"Error SQL: {e}")

    if st.button("🔗 Mostrar ejemplo JOIN (denuncias con departamento y modalidad)"):
        try:
            jtab, ok = obtener_denuncias_join(limite=200)
            if ok and jtab is not None:
                st.dataframe(jtab, use_container_width=True)
            else:
                st.warning("⚠️ No hay datos o carga la BD primero")
        except Exception as e:
            st.error(f"❌ Error mostrando JOIN: {e}")
            logger.exception(f"Error JOIN: {e}")

with tab_tabla:
    if st.button("Cargar tabla completa desde BD"):
        try:
            tabla, exito = obtener_tabla_completa(limite=500)
            if exito and tabla is not None:
                st.dataframe(tabla, use_container_width=True)
                st.caption(f"Total de filas mostradas: {len(tabla)}")
            else:
                st.warning("⚠️ Carga datos a la BD primero")
        except Exception as e:
            st.error(f"❌ Error: {e}")
            logger.exception(f"Error: {e}")

st.divider()

st.subheader("Tablas creadas y vista JOIN")
try:
    tablas_df, ok_tablas = consultar_bd(
        "SELECT name AS tabla FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    if ok_tablas and tablas_df is not None and not tablas_df.empty:
        st.dataframe(tablas_df, use_container_width=True)
        table_names = tablas_df["tabla"].tolist()
        selected_table = st.selectbox("Ver tabla individual", options=table_names)
        if selected_table:
            try:
                data_df, ok_data = consultar_bd(f"SELECT * FROM {selected_table} LIMIT 500")
                if ok_data and data_df is not None:
                    st.dataframe(data_df, use_container_width=True)
                    st.caption(f"Mostrando hasta 500 filas de `{selected_table}`.")
                else:
                    st.warning("⚠️ Sin datos para la tabla seleccionada.")
            except Exception as e:
                st.error(f"❌ No se pudo mostrar la tabla {selected_table}: {e}")
    else:
        st.info("ℹ️ Aún no hay tablas registradas. Carga datos a la BD para verlas aquí.")
except Exception as e:
    st.error(f"❌ No se pudieron listar las tablas: {e}")
    logger.exception(f"Error listando tablas: {e}")

if st.button("Mostrar JOIN de todas las tablas", key="join_full_btn"):
    try:
        join_df, ok_join = obtener_denuncias_join(limite=300)
        if ok_join and join_df is not None and not join_df.empty:
            st.dataframe(join_df, use_container_width=True)
            st.caption("Vista combinada de denuncias, departamentos y modalidades.")
        else:
            st.warning("⚠️ No existen registros combinados para mostrar.")
    except Exception as e:
        st.error(f"❌ Error obteniendo el JOIN: {e}")
        logger.exception(f"Error JOIN completo: {e}")

st.divider()


# ====== RESTO DE LA APP (CÓDIGO ORIGINAL) ======
# Carga de datos parametrizada (caché por ruta)
@st.cache_data(show_spinner=False)
def load_data(path_str: str) -> pd.DataFrame:
    from pathlib import Path
    try:
        df = clean(load_raw(Path(path_str)))
        logger.info(f"Datos cargados en cache: {Path(path_str).name}")
        return df
    except Exception as e:
        logger.exception(f"Error cargando datos en cache: {e}")
        st.error(f"Error cargando datos: {e}")
        return None


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
        st.caption(f"📄 Archivo de datos seleccionado: `{dp.name}` — modificado: {ts}")
    else:
        st.caption(f"📄 Archivo de datos seleccionado: `{dp.name}` (no existe aún)")
except Exception:
    pass

# KPIs desde la base de datos (si hay datos)
try:
    stats_df, ok = obtener_estadisticas_generales()
    if ok and stats_df is not None and not stats_df.empty:
        row = stats_df.iloc[0]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📅 Años en BD", int(row["años"]))
        k2.metric("🗺️ Departamentos", int(row["departamentos"]))
        k3.metric("📋 Modalidades", int(row["modalidades"]))
        k4.metric("📊 Total denuncias", int(row["total_denuncias"]))
except Exception as e:
    logger.warning(f"Error mostrando KPIs de BD: {e}")

# Cargar DataFrame usando la ruta seleccionada
try:
    df = load_data(str(dp))
    if df is None:
        st.stop()
except FileNotFoundError:
    st.error("❌ Archivo seleccionado no encontrado. Descarga el CSV o elige otro archivo.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    logger.exception(f"Error cargando datos: {e}")
    st.stop()


# Controles (≥3): año, modalidades, departamento, provincia dependiente, rango de meses
years = sorted([int(x) for x in df["AÑO"].dropna().unique()])
mods = sorted([m for m in df["MODALIDADES"].dropna().unique()])
dptos = sorted([d for d in df["DEPARTAMENTO"].dropna().unique()])


st.subheader("🎛️ Filtros de Análisis")
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

# Controles adicionales
st.subheader("📋 Controles Adicionales")
col_extra1, col_extra2, col_extra3 = st.columns(3)

with col_extra1:
    show_distritos = st.checkbox("Filtrar por Distrito", value=False)
    dist_sel = None
    if show_distritos and dpto_sel != "Todos":
        distritos = sorted([d for d in df[df["DEPARTAMENTO"] == dpto_sel]["DISTRITO"].dropna().unique()])
        dist_sel = st.selectbox("Distrito", options=["Todos"] + distritos, index=0)
        dist_sel = None if dist_sel == "Todos" else dist_sel

with col_extra2:
    export_data = st.checkbox("Exportar datos filtrados", value=False)

with col_extra3:
    show_correlation = st.checkbox("Mostrar matriz de correlación", value=False)

# Aplicar filtros
try:
    df_f = filter_df(df, year_sel, mods_sel, dpto_sel, prov_sel, mes_sel)
    
    # Filtro adicional de distrito si se aplicó
    if dist_sel and "DISTRITO" in df_f.columns:
        df_f = df_f[df_f["DISTRITO"] == dist_sel]
    
    logger.info(f"Filtros aplicados: {len(df_f)} filas resultantes")
except Exception as e:
    st.error(f"❌ Error aplicando filtros: {e}")
    logger.exception(f"Error en filtros: {e}")
    df_f = df.copy()


# Indicador simple de total filtrado
total_denuncias = int(df_f["cantidad"].sum())
st.metric("📊 Total de denuncias (filtro activo)", total_denuncias)

# Exportar datos filtrados si se solicita
if export_data:
    try:
        csv_export = df_f.to_csv(index=False)
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv_export,
            file_name="denuncias_filtradas.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"❌ Error exportando datos: {e}")
        logger.exception(f"Error exportando: {e}")


# Tabla principal
st.subheader("📊 Tabla filtrada")
st.dataframe(
    df_f[["AÑO", "MES", "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "MODALIDADES", "cantidad"]]
    .sort_values(["MES", "cantidad"], ascending=[True, False]),
    use_container_width=True
)


# ====== GRÁFICOS INTERACTIVOS ======
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Denuncias por modalidad")
    try:
        st.altair_chart(bar_modalidad(by_modalidad(df_f)), use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error en gráfico de modalidades: {e}")
        logger.exception(f"Error gráfico modalidades: {e}")

with col2:
    st.subheader("📉 Tendencia mensual")
    try:
        st.altair_chart(line_trend(monthly_trend(df_f)), use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error en gráfico de tendencia: {e}")
        logger.exception(f"Error gráfico tendencia: {e}")


st.subheader("🏆 Top 10 departamentos")
try:
    st.altair_chart(bar_top_departamentos(top_departamentos(df_f)), use_container_width=True)
except Exception as e:
    st.error(f"❌ Error en top departamentos: {e}")
    logger.exception(f"Error top departamentos: {e}")


# ====== ANÁLISIS AVANZADO ======
st.divider()
st.subheader("🔬 Análisis Avanzado")

tab_predict, tab_growth, tab_corr = st.tabs(["📊 Predicciones", "📈 Crecimiento", "🔗 Correlaciones"])

with tab_predict:
    st.write("**Predicción de tendencia mensual (regresión lineal simple)**")
    months_ahead = st.slider("Meses a predecir", min_value=1, max_value=12, value=3)
    
    try:
        pred_df = predict_monthly_trend(df_f, months_ahead=months_ahead)
        if pred_df is not None and not pred_df.empty:
            # Combinar datos históricos + predicciones
            monthly = monthly_trend(df_f)
            monthly["es_prediccion"] = False
            
            combined = pd.concat([monthly, pred_df], ignore_index=True)
            
            st.dataframe(pred_df[["MES", "cantidad_predicha"]], use_container_width=True)
            
            # Visualizar con Altair
            import altair as alt
            chart = alt.Chart(combined).mark_line(point=True).encode(
                x=alt.X("MES:Q", title="Mes"),
                y=alt.Y("cantidad_predicha:Q" if "cantidad_predicha" in combined.columns else "cantidad:Q", title="Denuncias"),
                color=alt.Color("es_prediccion:N", scale=alt.Scale(domain=[False, True], range=["#1f77b4", "#ff7f0e"]), legend=alt.Legend(title="Tipo")),
                tooltip=["MES", alt.Tooltip("cantidad_predicha:Q" if "cantidad_predicha" in combined.columns else "cantidad:Q", title="Denuncias")]
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos suficientes para predicción")
    except Exception as e:
        st.warning(f"⚠️ Error en predicción: {e}")
        logger.exception(f"Error predicción: {e}")

with tab_growth:
    st.write("**Análisis de crecimiento (tasa de cambio)**")
    
    growth_period = st.radio("Período de análisis", options=["Anual", "Mensual", "Por Modalidad"], horizontal=True)
    
    try:
        period_map = {"Anual": "anio", "Mensual": "mes", "Por Modalidad": "modalidad"}
        growth_df = calculate_growth_rate(df_f, period=period_map[growth_period])
        
        if growth_df is not None and not growth_df.empty:
            st.dataframe(growth_df, use_container_width=True)
            
            # Visualizar
            import altair as alt
            if growth_period == "Anual":
                x_field, y_field = "AÑO:Q", "growth_rate:Q"
                title = "Crecimiento Anual (%)"
            elif growth_period == "Mensual":
                x_field, y_field = "MES:O", "growth_rate:Q"
                title = "Crecimiento Mensual (%)"
            else:
                x_field, y_field = "MODALIDADES:N", "growth_rate:Q"
                title = "Crecimiento por Modalidad (%)"
            
            chart = alt.Chart(growth_df).mark_bar().encode(
                x=alt.X(x_field, title=""),
                y=alt.Y(y_field, title="Tasa de Crecimiento (%)"),
                color=alt.condition(alt.datum.growth_rate > 0, alt.value("#2ca02c"), alt.value("#d62728")),
                tooltip=["growth_rate"]
            ).properties(height=300, title=title)
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos para cálculo de crecimiento")
    except Exception as e:
        st.warning(f"⚠️ Error en crecimiento: {e}")
        logger.exception(f"Error growth: {e}")

with tab_corr:
    st.write("**Matriz de correlación: Modalidad vs Departamento**")
    
    try:
        corr_matrix = calculate_correlation_matrix(df_f)
        if corr_matrix is not None and not corr_matrix.empty:
            st.dataframe(corr_matrix.round(3), use_container_width=True)
            
            # Heatmap
            import altair as alt
            corr_flat = corr_matrix.reset_index().melt(id_vars="DEPARTAMENTO")
            corr_flat.columns = ["DEPARTAMENTO", "MODALIDAD", "Correlacion"]
            
            heatmap = alt.Chart(corr_flat).mark_rect().encode(
                x=alt.X("MODALIDAD:N", title="Modalidad"),
                y=alt.Y("DEPARTAMENTO:N", title="Departamento"),
                color=alt.Color("Correlacion:Q", scale=alt.Scale(scheme="blues"), title="Correlación"),
                tooltip=["DEPARTAMENTO", "MODALIDAD", "Correlacion"]
            ).properties(height=400, width=600)
            
            st.altair_chart(heatmap, use_container_width=True)
        else:
            st.info("ℹ️ No hay datos para matriz de correlación")
    except Exception as e:
        st.info(f"ℹ️ No se pudo calcular correlación: {e}")
        logger.exception(f"Error correlación: {e}")


st.divider()

# Nota final de citación
st.caption("📚 Datos 2018–2025, cortes mensuales; procedencia y variables según diccionario y metadatos de SIDPOL/SIDPPOL – MININTER.")
