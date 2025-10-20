import altair as alt
import pandas as pd

# Paleta fija por modalidad (basado en las categorías del diccionario)
MOD_ORDER = [
    "Homicidio",
    "Robo",
    "Hurto",
    "Estafa",
    "Extorsión",
    "Violencia contra la mujer e integrantes",
    "Otros",
]
MOD_COLORS = [
    "#b30000",  # Homicidio
    "#1f77b4",  # Robo
    "#2ca02c",  # Hurto
    "#ff7f0e",  # Estafa
    "#9467bd",  # Extorsión
    "#d62728",  # Violencia contra la mujer e integrantes
    "#7f7f7f",  # Otros
]
MOD_SCALE = alt.Scale(domain=MOD_ORDER, range=MOD_COLORS)

def bar_modalidad(df: pd.DataFrame):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("MODALIDADES:N", sort="-y", title="Modalidad"),
            y=alt.Y("cantidad:Q", title="Denuncias"),
            color=alt.Color("MODALIDADES:N", scale=MOD_SCALE, legend=alt.Legend(title="Modalidad")),
            tooltip=["MODALIDADES","cantidad"]
        )
        .properties(height=320)
    )

# Si tienes otro gráfico de barras por MODALIDADES, aplica la misma color scale:
def bar_modalidad_por_depto(df: pd.DataFrame):
    # ejemplo opcional: barras apiladas por modalidad dentro de departamento
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("DEPARTAMENTO:N", title="Departamento"),
            y=alt.Y("cantidad:Q", title="Denuncias"),
            color=alt.Color("MODALIDADES:N", scale=MOD_SCALE, legend=alt.Legend(title="Modalidad")),
            tooltip=["DEPARTAMENTO","MODALIDADES","cantidad"]
        )
        .properties(height=320)
    )