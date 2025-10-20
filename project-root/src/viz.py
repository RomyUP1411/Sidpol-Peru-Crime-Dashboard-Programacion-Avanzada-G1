import altair as alt
import pandas as pd

def bar_modalidad(df: pd.DataFrame):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(x=alt.X("P_MODALIDADES:N", sort="-y", title="Modalidad"),
                y=alt.Y("cantidad:Q", title="Denuncias"),
                tooltip=["P_MODALIDADES","cantidad"])
        .properties(height=320)
    )  # gráfico simple exigido por la guía [file:2]

def line_trend(df: pd.DataFrame):
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(x=alt.X("MES:O", title="Mes"),
                y=alt.Y("cantidad:Q", title="Denuncias"),
                tooltip=["MES","cantidad"])
        .properties(height=280)
    )  # tendencia mensual con meses del CSV [file:23]

def bar_top_departamentos(df: pd.DataFrame):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(y=alt.Y("DPTO_HECHO_NEW:N", sort="-x", title="Departamento"),
                x=alt.X("cantidad:Q", title="Denuncias"),
                tooltip=["DPTO_HECHO_NEW","cantidad"])
        .properties(height=320)
    )  # top 10 departamentos según agregación [file:23]

def heatmap_mod_mes(df: pd.DataFrame):
    return (
        alt.Chart(df)
        .mark_rect()
        .encode(x=alt.X("MES:O", title="Mes"),
                y=alt.Y("P_MODALIDADES:N", title="Modalidad"),
                color=alt.Color("cantidad:Q", title="Denuncias"),
                tooltip=["P_MODALIDADES","MES","cantidad"])
        .properties(height=320)
    )  # matriz modalidad x mes para patrones de estacionalidad [file:23][file:24]