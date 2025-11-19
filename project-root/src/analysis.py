"""
Módulo de análisis y predicción para denuncias SIDPOL.
Incluye regresión temporal simple y análisis avanzado.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from typing import Tuple, Optional
from utils import log_time, logger
from exceptions import ProcessingError


@log_time
def predict_monthly_trend(df: pd.DataFrame, months_ahead: int = 3) -> Optional[pd.DataFrame]:
    """
    Predice denuncias para los próximos N meses usando regresión lineal.
    
    Args:
        df: DataFrame con MES y cantidad.
        months_ahead: Número de meses a predecir.
    
    Returns:
        DataFrame con predicciones o None si hay error.
    """
    try:
        if df.empty:
            logger.warning("DataFrame vacío para predicción")
            return None
        
        # Agrupar por mes si no está ya agregado
        monthly = df.groupby("MES", as_index=False)["cantidad"].sum()
        
        if len(monthly) < 2:
            logger.warning("Datos insuficientes para predicción (< 2 meses)")
            return None
        
        # Preparar datos para regresión
        X = monthly["MES"].values.reshape(-1, 1)
        y = monthly["cantidad"].values
        
        # Entrenar modelo lineal simple
        model = LinearRegression()
        model.fit(X, y)
        
        # Generar predicciones para próximos meses
        last_month = monthly["MES"].max()
        future_months = np.array([last_month + i for i in range(1, months_ahead + 1)]).reshape(-1, 1)
        predictions = model.predict(future_months)
        
        # Crear DataFrame de resultados
        result = pd.DataFrame({
            "MES": future_months.flatten(),
            "cantidad_predicha": predictions,
            "es_prediccion": True
        })
        
        logger.info(f"Predicción generada para {months_ahead} meses")
        return result
    
    except Exception as e:
        logger.exception(f"Error en predicción de tendencia: {e}")
        raise ProcessingError(f"No se pudo predecir tendencia: {e}")


@log_time
def calculate_growth_rate(df: pd.DataFrame, period: str = "anio") -> Optional[pd.DataFrame]:
    """
    Calcula tasa de crecimiento YoY o por período.
    
    Args:
        df: DataFrame con AÑO y cantidad.
        period: "anio", "mes" o "modalidad".
    
    Returns:
        DataFrame con tasas de crecimiento.
    """
    try:
        if df.empty or period not in ["anio", "mes", "modalidad"]:
            return None
        
        if period == "anio":
            yearly = df.groupby("AÑO", as_index=False)["cantidad"].sum()
            yearly["growth_rate"] = yearly["cantidad"].pct_change() * 100
            return yearly
        elif period == "mes":
            monthly = df.groupby("MES", as_index=False)["cantidad"].sum()
            monthly["growth_rate"] = monthly["cantidad"].pct_change() * 100
            return monthly
        elif period == "modalidad":
            by_mod = df.groupby("MODALIDADES", as_index=False)["cantidad"].sum()
            by_mod["growth_rate"] = by_mod["cantidad"].pct_change() * 100
            return by_mod
    
    except Exception as e:
        logger.exception(f"Error calculando growth rate: {e}")
        return None


@log_time
def top_modalidad_by_departamento(df: pd.DataFrame, n: int = 5) -> Optional[pd.DataFrame]:
    """
    Retorna top N modalidades por cada departamento.
    
    Args:
        df: DataFrame con DEPARTAMENTO, MODALIDADES y cantidad.
        n: Número de modalidades a retornar por departamento.
    
    Returns:
        DataFrame filtrado con top N.
    """
    try:
        if df.empty:
            return None
        
        result = (
            df.groupby(["DEPARTAMENTO", "MODALIDADES"], as_index=False)["cantidad"].sum()
            .sort_values(["DEPARTAMENTO", "cantidad"], ascending=[True, False])
            .groupby("DEPARTAMENTO")
            .head(n)
        )
        logger.info(f"Calculado top {n} modalidades por departamento")
        return result
    
    except Exception as e:
        logger.exception(f"Error en top modalidad por departamento: {e}")
        return None


def calculate_correlation_matrix(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Calcula matriz de correlación entre modalidades y departamentos (en términos de cantidad).
    Usa pivot table para crear una matriz numérica.
    
    Returns:
        Matriz de correlación o None.
    """
    try:
        if df.empty or "MODALIDADES" not in df.columns or "DEPARTAMENTO" not in df.columns:
            return None
        
        pivot = df.pivot_table(
            index="DEPARTAMENTO",
            columns="MODALIDADES",
            values="cantidad",
            aggfunc="sum",
            fill_value=0
        )
        
        corr_matrix = pivot.corr()
        logger.info("Matriz de correlación calculada")
        return corr_matrix
    
    except Exception as e:
        logger.exception(f"Error calculando correlación: {e}")
        return None
