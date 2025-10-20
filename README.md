Prototipo en Streamlit para explorar denuncias policiales del Perú a partir de un CSV con limpieza básica, filtros y visualizaciones descriptivas, correspondiente a la entrega parcial del curso Programación Avanzada en Ciencia de Datos. [file:2]

## ¿Qué hace?
- Carga el CSV oficial de denuncias (2018–2025), tipifica columnas y renombra encabezados para una visualización legible en la interfaz. [file:23][file:24]
- Permite filtrar por Año, Modalidades, Departamento, Provincia y rango de Mes, mostrando tabla y gráficos interactivos. [file:2][file:24]
- Incluye tres visualizaciones: barras por modalidad, tendencia mensual y top 10 departamentos, con paleta fija por modalidad. [file:2][file:24]

## Datos y licencia
- Fuente: Sistema de Denuncias Policiales SIDPOL/SIDPPOL – MININTER. [file:25]
- Variables utilizadas: AÑO, MES, DEPARTAMENTO, PROVINCIA, DISTRITO, MODALIDADES, cantidad, conforme al diccionario del recurso. [file:24]
- Licencia: uso con atribución (ODC-By) según metadatos del recurso. [file:25]

## Estructura del repositorio
- data/: CSV y documentación de datos (diccionario y metadatos). [file:23][file:24][file:25]
- src/: código de la app (app.py), procesamiento (processing.py) y visualizaciones (viz.py). [file:2]
- docs/ (opcional): capturas y documento del parcial para entrega. [file:2]

## Requisitos
- Python 3.10+ y entorno virtual (.venv) con Streamlit, Pandas, Altair y PyArrow. [file:2]
- requirements.txt con dependencias mínimas para reproducibilidad local. [file:2]

## Ejecución local (Windows PowerShell)

1) Clonar o descargar el repo y abrirlo en VS Code ubicándote en la carpeta raíz donde están data/ y src/ para que las rutas relativas funcionen.​
2) Crear el entorno virtual (solo la primera vez en cada equipo):
    python -m venv .venv​
3) Activar el entorno virtual:
    PowerShell: Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
    y luego .venv\Scripts\Activate.ps1​
    
    CMD: ..venv\Scripts\activate.bat​
    
    macOS/Linux: source .venv/bin/activate​

4) Instalar dependencias (primera vez o si cambió requirements.txt):
    pip install -r requirements.txt​
5) Ejecutar la app de Streamlit desde la raíz del proyecto:
    streamlit run src/app.py​

Abrir el navegador en http://localhost:8501; usar los controles para filtrar por Año, Modalidades, Departamento, Provincia y Mes, viendo tabla y gráficos.
