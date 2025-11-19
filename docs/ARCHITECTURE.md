# 📐 Arquitectura - Dashboard SIDPOL Perú

## 📋 Descripción General

Sistema completo de análisis de denuncias policiales del Perú (SIDPOL) con:
- **Datos externos**: Descarga desde `datosabiertos.gob.pe` (API responsable con reintentos y backoff)
- **Persistencia**: SQLite con esquema normalizado (4 tablas relacionadas)
- **Análisis**: Procesamiento de datos + modelos de predicción (regresión lineal)
- **Dashboard**: Streamlit interactivo con múltiples visualizaciones y controles
- **Calidad**: Manejo exhaustivo de errores, decoradores, logging, estructura modular

---

## 🗂️ Estructura de Archivos

```
project-root/
├── src/
│   ├── app.py                 # Aplicación Streamlit principal
│   ├── database.py            # Gestión de BD SQLite (CRUD, JOINs)
│   ├── processing.py          # Transformación y limpieza de datos
│   ├── download_data.py       # Descarga de datos desde API externa
│   ├── viz.py                 # Visualizaciones con Altair
│   ├── analysis.py            # Análisis avanzado (predicción, correlación)
│   ├── utils.py               # Decoradores (log_time, debug, cache_result, handle_errors) + logging
│   └── exceptions.py          # Excepciones personalizadas
├── data/
│   ├── DATASET_Denuncias_Policiales_*.csv  # Archivos CSV
│   ├── denuncias.db           # Base de datos SQLite
│   ├── metadata.json          # Metadatos de descarga (sha256, size, fecha)
│   └── sidpol.log             # Log de aplicación
├── docs/
│   └── ARCHITECTURE.md        # Este archivo
├── logs/
│   └── sidpol.log             # Logs de ejecución
├── requirements.txt           # Dependencias Python
└── README.md                  # Instrucciones de uso
```

---

## 🔌 Integración de Datos Externos (API/Web Scraping)

### URL Base
```
https://www.datosabiertos.gob.pe/sites/default/files/DATASET_Denuncias_Policiales_Enero%202018%20a%20Octubre%202025.csv
```

### Características
- **Método**: `requests.get()` con User-Agent
- **Reintentos**: 3 intentos con backoff exponencial (1s, 2s, 4s)
- **Metadatos**: Se guardan en `data/metadata.json`:
  - `filename`: nombre del archivo descargado
  - `url`: URL fuente
  - `downloaded_at`: timestamp ISO
  - `sha256`: hash del contenido
  - `size_bytes`: tamaño en bytes
  - `columns_standardized`: indica si las columnas fueron normalizadas

### Validación
- Detección automática de encoding (UTF-8 → Latin-1 fallback)
- Mapeo inteligente de nombres de columnas
- Verificación de esquema esperado

---

## 💾 Base de Datos SQLite

### Ubicación
`data/denuncias.db`

### Esquema (4 tablas relacionadas)

#### 1. `fuentes`
```sql
CREATE TABLE fuentes (
    id INTEGER PRIMARY KEY,
    filename TEXT UNIQUE,
    url TEXT,
    downloaded_at TEXT,
    sha256 TEXT,
    size_bytes INTEGER
);
```
**Propósito**: Rastrear archivos descargados y metadatos

#### 2. `departamentos`
```sql
CREATE TABLE departamentos (
    id INTEGER PRIMARY KEY,
    nombre TEXT UNIQUE
);
```
**Propósito**: Valores únicos de departamentos (normalización)

#### 3. `modalidades`
```sql
CREATE TABLE modalidades (
    id INTEGER PRIMARY KEY,
    nombre TEXT UNIQUE
);
```
**Propósito**: Valores únicos de modalidades delictivas (normalización)

#### 4. `denuncias` (tabla hechos)
```sql
CREATE TABLE denuncias (
    id INTEGER PRIMARY KEY,
    anio INTEGER,
    mes INTEGER,
    departamento_id INTEGER,
    provincia TEXT,
    distrito TEXT,
    modalidad_id INTEGER,
    cantidad INTEGER,
    fuente_id INTEGER,
    FOREIGN KEY(departamento_id) REFERENCES departamentos(id),
    FOREIGN KEY(modalidad_id) REFERENCES modalidades(id),
    FOREIGN KEY(fuente_id) REFERENCES fuentes(id)
);
```
**Propósito**: Tabla principal de denuncias con referencias de integridad

### Consultas Principales

```python
# Denuncias por modalidad
SELECT m.nombre, SUM(d.cantidad) 
FROM denuncias d
LEFT JOIN modalidades m ON d.modalidad_id = m.id
GROUP BY m.nombre;

# Top departamentos
SELECT dep.nombre, SUM(d.cantidad)
FROM denuncias d
LEFT JOIN departamentos dep ON d.departamento_id = dep.id
GROUP BY dep.nombre
ORDER BY SUM(d.cantidad) DESC LIMIT 10;

# JOIN completo (ejemplo)
SELECT d.id, d.anio, d.mes, dep.nombre, mod.nombre, d.cantidad
FROM denuncias d
LEFT JOIN departamentos dep ON d.departamento_id = dep.id
LEFT JOIN modalidades mod ON d.modalidad_id = mod.id;
```

---

## 📊 Procesamiento y Análisis

### Módulo `processing.py`

**Funciones de carga y limpieza:**
- `load_raw()`: Lee CSV con encoding automático
- `clean()`: Tipificación, renombrado de columnas, filtrado de NaN
- `filter_df()`: Filtro multidimensional (año, modalidades, dpto, provincia, mes)

**Agregaciones para visualización:**
- `by_modalidad()`: Agrupa por modalidad
- `monthly_trend()`: Agrupa por mes (1-12)
- `top_departamentos()`: Top 10 departamentos
- `heatmap_modalidad_mes()`: Matriz modalidad × mes

### Módulo `analysis.py`

**Modelo predictivo:**
```python
predict_monthly_trend(df, months_ahead=3)
```
- Usa `LinearRegression` de scikit-learn
- Entrena con datos históricos mensuales
- Predice N meses hacia adelante
- Retorna DataFrame con predicciones

**Análisis de crecimiento:**
```python
calculate_growth_rate(df, period="anio|mes|modalidad")
```
- Calcula `pct_change()` acumulativo
- Retorna tasa de crecimiento (%)
- Soporta análisis por período

**Análisis de correlación:**
```python
calculate_correlation_matrix(df)
```
- Crea matriz de pivot (departamentos × modalidades)
- Calcula correlación de Pearson
- Visualizable como heatmap

---

## 🎨 Dashboard Streamlit

### Secciones Principales

#### 1. **Login y Usuario**
- Sesión temporal guardada en `st.session_state`
- Tracking de usuario en logs

#### 2. **Descarga de Datos**
- Botón para descargar desde `datosabiertos.gob.pe`
- Reintentos automáticos con backoff
- Validación de columnas

#### 3. **Gestión de Base de Datos**
- Cargar CSV a BD
- Ver estadísticas generales (años, dpto, modalidades, total)
- Actualizar caché

#### 4. **Editor SQL**
- Ejecutar consultas personalizadas
- Mostrar JOINs de ejemplo
- Listar y navegar tablas

#### 5. **Filtros Interactivos**
- Año (selectbox)
- Modalidades (multiselect)
- Departamento (selectbox con provincia dependiente)
- Rango de meses (slider)
- **Adicionales**: Distrito, exportar CSV, correlación

#### 6. **Visualizaciones Principales**
- 📊 Barras: Denuncias por modalidad
- 📈 Línea: Tendencia mensual
- 🏆 Top 10 departamentos

#### 7. **Análisis Avanzado** (3 pestañas)
- **Predicciones**: Regresión lineal con gráfico
- **Crecimiento**: Tasas YoY/mensual por modalidad
- **Correlaciones**: Matriz de correlación (heatmap)

### KPIs Mostrados
- Total denuncias (en tiempo real)
- Años en BD
- Departamentos únicos
- Modalidades únicas
- Métricas de crecimiento

---

## 🛡️ Manejo de Errores y Calidad

### Excepciones Personalizadas (`exceptions.py`)
```python
SIDPOLException        # Base
├── DataLoadError       # Errores al cargar
├── DatabaseError       # Errores BD
├── DownloadError       # Errores descarga
├── ProcessingError     # Errores procesamiento
└── ValidationError     # Errores validación
```

### Decoradores Avanzados (`utils.py`)

```python
@log_time              # Registra tiempo de ejecución
@debug                 # Loguea args, kwargs, resultado
@cache_result          # Cachea resultados en sesión
@handle_errors(None)   # Captura excepciones sin propagar
```

### Logging Centralizado
- **Archivo**: `logs/sidpol.log`
- **Nivel**: DEBUG (archivo) + INFO (consola)
- **Formato**: `timestamp [LEVEL] module: message`
- **Módulos**: Cada módulo importa `logger` de `utils`

---

## 🔄 Flujo de Datos

```
datosabiertos.gob.pe (CSV)
        ↓
download_data.py (requests + reintentos)
        ↓
data/DATASET_*.csv
        ↓
processing.py (load_raw → clean → filter_df)
        ↓
Pandas DataFrame (en memoria)
        ↓
database.py (cargar_csv_a_bd) ←→ data/denuncias.db
        ↓
app.py (Streamlit)
  ├→ viz.py (gráficos Altair)
  ├→ analysis.py (predicción, correlación)
  └→ database.py (consultas SQL)
        ↓
Navegador (usuario interactúa)
```

---

## 📦 Dependencias

| Paquete | Versión | Uso |
|---------|---------|-----|
| streamlit | >=1.36 | Framework dashboard |
| pandas | >=2.2 | Manipulación de datos |
| altair | >=5.3 | Visualizaciones interactivas |
| requests | latest | Descarga de datos |
| scikit-learn | >=1.3 | Regresión lineal |
| numpy | >=1.24 | Cálculos numéricos |
| pyarrow | >=16.0 | Serialización eficiente |

---

## 🚀 Ejecución

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecutar Streamlit
```bash
streamlit run src/app.py
```

### Ver Logs
```bash
tail -f logs/sidpol.log
```

---

## 🔐 Seguridad y Mejores Prácticas

- ✅ **SQL Injection**: Uso de parámetros (`?`) en consultas
- ✅ **User-Agent**: Identificación responsable en descargas
- ✅ **Reintentos**: Backoff exponencial para respetar servidores
- ✅ **Caching**: Decorador `@cache_result` para optimizar
- ✅ **Validación**: Tipificación exhaustiva de datos
- ✅ **Logging**: Trazabilidad completa de operaciones
- ✅ **Modularidad**: Separación de responsabilidades

---

## 📝 Cumplimiento de Requisitos 3.2 (60%)

| Criterio | Implementación |
|----------|-----------------|
| **Datos externos** | ✅ API `datosabiertos.gob.pe` con reintentos y metadatos |
| **Persistencia** | ✅ SQLite con 4 tablas relacionadas, FK, JOINs |
| **Procesamiento** | ✅ Limpieza, tipificación, filtros, agregaciones |
| **Análisis** | ✅ Regresión lineal, growth rate, correlación |
| **Streamlit** | ✅ 6+ visualizaciones, 10+ controles interactivos |
| **KPIs** | ✅ Métricas en tiempo real, crecimiento, tendencias |
| **Manejo errores** | ✅ Try/except exhaustivos, excepciones personalizadas |
| **Decoradores** | ✅ log_time, debug, cache_result, handle_errors |
| **Estructura modular** | ✅ 8 módulos independientes con responsabilidades claras |

---

**Última actualización**: Noviembre 2025  
**Autor**: Equipo de desarrollo SIDPOL Dashboard
