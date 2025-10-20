# src/viz.py
from __future__ import annotations

import altair as alt
import pandas as pd

# Orden y paleta fija por modalidades (conforme a categorías del recurso)
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


# Barras por modalidad con color consistente
def bar_modalidad(df: pd.DataFrame) -> alt.Chart:
    base = alt.Chart(df)
    return (
        base.mark_bar()
        .encode(
            x=alt.X("MODALIDADES:N", sort="-y", title="Modalidad"),
            y=alt.Y("cantidad:Q", title="Denuncias"),
            color=alt.Color("MODALIDADES:N", scale=MOD_SCALE, legend=alt.Legend(title="Modalidad")),
            tooltip=[alt.Tooltip("MODALIDADES:N", title="Modalidad"), alt.Tooltip("cantidad:Q", title="Denuncias")],
        )
        .properties(height=320)
    )


# Línea de tendencia mensual (1–12)
def line_trend(df: pd.DataFrame) -> alt.Chart:
    base = alt.Chart(df)
    return (
        base.mark_line(point=True)
        .encode(
            x=alt.X("MES:O", title="Mes"),
            y=alt.Y("cantidad:Q", title="Denuncias"),
            tooltip=[alt.Tooltip("MES:O", title="Mes"), alt.Tooltip("cantidad:Q", title="Denuncias")],
        )
        .properties(height=280)
    )


# Top N departamentos por total
def bar_top_departamentos(df: pd.DataFrame, title: str | None = None) -> alt.Chart:
    base = alt.Chart(df)
    chart = (
        base.mark_bar()
        .encode(
            y=alt.Y("DEPARTAMENTO:N", sort="-x", title="Departamento"),
            x=alt.X("cantidad:Q", title="Denuncias"),
            tooltip=[alt.Tooltip("DEPARTAMENTO:N", title="Departamento"), alt.Tooltip("cantidad:Q", title="Denuncias")],
        )
        .properties(height=320)
    )
    if title:
        chart = chart.properties(title=title)
    return chart


# Heatmap modalidad x mes
def heatmap_mod_mes(df: pd.DataFrame) -> alt.Chart:
    base = alt.Chart(df)
    return (
        base.mark_rect()
        .encode(
            x=alt.X("MES:O", title="Mes"),
            y=alt.Y("MODALIDADES:N", title="Modalidad"),
            color=alt.Color("cantidad:Q", title="Denuncias"),
            tooltip=[
                alt.Tooltip("MODALIDADES:N", title="Modalidad"),
                alt.Tooltip("MES:O", title="Mes"),
                alt.Tooltip("cantidad:Q", title="Denuncias"),
            ],
        )
        .properties(height=320)
    )