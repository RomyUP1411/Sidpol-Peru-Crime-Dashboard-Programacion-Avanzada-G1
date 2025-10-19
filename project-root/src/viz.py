import altair as alt
import pandas as pd

def bar_modalidad(df: pd.DataFrame):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("P_MODALIDADES:N", sort="-y", title="Modalidad"),
            y=alt.Y("cantidad:Q", title="Denuncias"),
            tooltip=["P_MODALIDADES","cantidad"]
        )
        .properties(height=320)
    )

def line_trend(df: pd.DataFrame):
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("MES:O", title="Mes"),
            y=alt.Y("cantidad:Q", title="Denuncias"),
            tooltip=["MES","cantidad"]
        )
        .properties(height=280)
    )