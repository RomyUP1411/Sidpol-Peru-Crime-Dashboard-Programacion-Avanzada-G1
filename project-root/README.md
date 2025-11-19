# SIDPOL Perú Crime Dashboard – Parcial

Prototipo en Streamlit para explorar denuncias policiales del Perú a partir de un CSV con limpieza básica, filtros y visualizaciones descriptivas, correspondiente a la entrega parcial del curso Programación Avanzada en Ciencia de Datos.

## ¿Qué hace?
- Carga el CSV local de denuncias (enero–diciembre 2018 2025), tipifica columnas y renombra encabezados para una visualización legible en la interfaz.
- Permite filtrar por Año, Modalidades, Departamento, Provincia y rango de Mes, mostrando tabla y gráficos interactivos.
- Incluye tres visualizaciones: barras por modalidad, tendencia mensual y top 10 departamentos, con paleta fija por modalidad.
- El alcance actual usa únicamente `src/app.py`, `src/processing.py` y `src/viz.py`; no hay scraping ni base SQLite.

## Datos y licencia
- Cobertura actual: denuncias enero-diciembre 2018 provistas en un único CSV en `data/`.
- Fuente: Sistema de Denuncias Policiales SIDPOL/SIDPPOL – MININTER.
- Variables utilizadas: AÑO, MES, DEPARTAMENTO, PROVINCIA, DISTRITO, MODALIDADES, cantidad, conforme al diccionario del recurso.
- Licencia: uso con atribución (ODC-By) según metadatos del recurso.

## Estructura del repositorio
- data/: CSV y documentación de datos (diccionario y metadatos).
- src/: código de la app (app.py), procesamiento (processing.py) y visualizaciones (viz.py).
- docs/ (opcional): capturas y documento del parcial para entrega.

## Requisitos
- Python 3.10+ y entorno virtual (.venv) con Streamlit, Pandas, Altair y PyArrow.
- requirements.txt con dependencias mínimas para reproducibilidad local.

## Ejecución local (Windows PowerShell)

1) Clonar o descargar el repo y abrirlo en VS Code en la carpeta raíz (donde están data/ y src/).​
2) Crear el entorno virtual desde el terminal en la carpeta del proyecto (solo la primera vez en cada equipo):

```python
python -m venv .venv
```

3) Activar el entorno virtual:

```python
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\.venv\Scripts\Activate.ps1
```

4) Instalar dependencias (primera vez o si cambió requirements.txt):

```python
pip install -r requirements.txt
```

5) Ejecutar la app de Streamlit:

```python
streamlit run src/app.py
```
- Se abrirá: http://localhost:8501 y usar los controles (Año, Modalidades, Departamento, Provincia, Mes).
- Para refrescar los datos, reemplaza el CSV en `data/` y vuelve a ejecutar la app.
