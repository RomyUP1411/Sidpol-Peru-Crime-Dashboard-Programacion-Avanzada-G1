# 🚔 SIDPOL Perú Crime Dashboard – Final (3.2)

**Prototipo profesional en Streamlit** para análisis y visualización de denuncias policiales del Perú (2018–2025) con integración de datos externos, persistencia en SQLite, análisis predictivo y dashboard interactivo completo.

**Entrega**: 3.2) Final (60%) – Programación Avanzada en Ciencia de Datos

---

## 🎯 Características Principales

### ✅ Datos Externos (API)
- Descarga responsable desde `datosabiertos.gob.pe` con reintentos automáticos y backoff exponencial
- Validación de encoding (UTF-8 → Latin-1 fallback)
- Metadatos completos: sha256, tamaño, timestamp

### ✅ Persistencia (SQLite)
- Base de datos normalizada con **4 tablas relacionadas**:
  - `fuentes`: metadatos de descarga
  - `departamentos`: valores únicos (normalización)
  - `modalidades`: valores únicos (normalización)
  - `denuncias`: tabla principal con claves foráneas
- Consultas SQL integradas, JOINs y vistas dinámicas

### ✅ Procesamiento y Análisis
- Limpieza y tipificación de datos (encoding, tipos numéricos)
- Filtros multidimensionales (año, modalidades, dpto, provincia, mes, distrito)
- **Análisis avanzado**:
  - Predicción con regresión lineal (scikit-learn)
  - Cálculo de tasas de crecimiento YoY/mensual
  - Matriz de correlación (modalidad vs departamento)

### ✅ Dashboard Streamlit (Completo)
- **6+ visualizaciones interactivas** (barras, líneas, heatmaps)
- **10+ controles dinámicos** (selectboxes, multiselect, sliders, checkboxes)
- **KPIs en tiempo real** (total, años, dpto, modalidades, crecimiento)
- **3 pestañas de análisis avanzado**
- Login de usuario y exportación de datos (CSV)
- Navegación clara y responsiva

### ✅ Calidad de Código
- **Try/except exhaustivos** en todos los módulos
- **Excepciones personalizadas** (`exceptions.py`)
- **4 decoradores avanzados**:
  - `@log_time`: tiempo de ejecución
  - `@debug`: logging de parámetros
  - `@cache_result`: cacheo en sesión
  - `@handle_errors`: captura silenciosa
- **Logging centralizado** a archivo + consola (DEBUG)
- **Estructura modular**: 8 módulos con responsabilidades claras

---

## 📋 ¿Qué hace?

1. **Descarga datos** desde el servidor oficial (datosabiertos.gob.pe)
2. **Carga en SQLite** con normalización automática
3. **Limpia y tipifica** columnas (encoding, tipos numéricos, strings)
4. **Filtra interactivamente** por múltiples dimensiones
5. **Visualiza gráficos** (modalidades, tendencias, top dpto)
6. **Predice tendencias** con regresión lineal
7. **Calcula correlaciones** y tasas de crecimiento
8. **Exporta datos** en CSV

---

## 📊 Datos y Licencia

- **Fuente**: Sistema de Denuncias Policiales SIDPOL/SIDPPOL – MININTER Perú
- **Período**: 2018 a octubre 2025 (actualizable)
- **Variables**: AÑO, MES, DEPARTAMENTO, PROVINCIA, DISTRITO, MODALIDADES, cantidad
- **Licencia**: ODC-By (atribución requerida)

---

## 🗂️ Estructura del Proyecto

```
project-root/
├── src/
│   ├── app.py                 # 🎨 Dashboard principal (Streamlit)
│   ├── database.py            # 💾 BD SQLite (CRUD, JOINs, consultas)
│   ├── processing.py          # 🔄 Transformación y limpieza
│   ├── download_data.py       # 📥 Descarga desde API
│   ├── viz.py                 # 📊 Visualizaciones (Altair)
│   ├── analysis.py            # 🔬 Análisis avanzado (predicción, correlación)
│   ├── utils.py               # 🛠️ Decoradores y logging
│   └── exceptions.py          # ⚠️ Excepciones personalizadas
├── data/
│   ├── DATASET_Denuncias_Policiales_*.csv  # 📄 Archivos CSV
│   ├── denuncias.db                        # 💾 Base de datos SQLite
│   ├── metadata.json                       # 📝 Metadatos descarga
│   └── [logs guardados aquí]
├── docs/
│   ├── ARCHITECTURE.md        # 📐 Documentación técnica detallada
│   └── [otros docs opcionales]
├── logs/
│   └── sidpol.log             # 📋 Log de ejecución
├── requirements.txt           # 📦 Dependencias
└── README.md                  # 📖 Este archivo
```

---

## 📦 Requisitos

- **Python 3.10+** con entorno virtual
- **Dependencias** (ver `requirements.txt`):
  - streamlit (>=1.36): framework web
  - pandas (>=2.2): análisis de datos
  - altair (>=5.3): visualizaciones
  - requests: descarga HTTP
  - scikit-learn (>=1.3): regresión lineal
  - numpy (>=1.24): cálculos numéricos
  - pyarrow (>=16.0): serialización

---

## 🚀 Ejecución Local (Windows PowerShell)

### 1. Clonar y configurar
```powershell
git clone <repo_url>
cd project-root
```

### 2. Crear entorno virtual (primera vez)
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 4. Ejecutar app
```powershell
streamlit run src/app.py
```

Se abrirá automáticamente en `http://localhost:8501`

### 5. (Opcional) Ver logs en tiempo real
```powershell
Get-Content logs/sidpol.log -Wait
```

---

## 🎮 Uso del Dashboard

### Secciones principales:

1. **👤 Usuario/Login**: Identificación temporal
2. **📥 Descarga CSV**: Obtener datos actualizados (con reintentos)
3. **⚙️ Gestión de BD**: Cargar a SQLite, ver estadísticas
4. **🔍 Editor SQL**: Consultas personalizadas y JOINs
5. **🎛️ Filtros**: Año, modalidades, dpto, provincia, mes, distrito
6. **📊 Visualizaciones**: 6+ gráficos interactivos
7. **🔬 Análisis avanzado**:
   - **Predicciones**: Tendencia futura (regresión lineal)
   - **Crecimiento**: Tasas YoY/mensual por modalidad
   - **Correlaciones**: Matriz de correlación (heatmap)

### Controles interactivos:
- Selectbox: Año, Departamento, Distrito
- Multiselect: Modalidades
- Slider: Rango de meses (1-12)
- Checkbox: Filtro de distrito, exportar CSV, correlación
- Botones: Descargar, cargar BD, ejecutar SQL

---

## 🛠️ Arquitectura Técnica

### Base de Datos (SQLite)

**Esquema (normalizado con FK)**:
```sql
-- Tabla de fuentes (metadatos)
fuentes(id, filename, url, downloaded_at, sha256, size_bytes)

-- Tablas de dimensión
departamentos(id, nombre)
modalidades(id, nombre)

-- Tabla de hechos
denuncias(id, anio, mes, departamento_id, provincia, distrito, 
          modalidad_id, cantidad, fuente_id [FK])
```

**Ejemplo de JOIN**:
```sql
SELECT d.anio, d.mes, dep.nombre, mod.nombre, d.cantidad
FROM denuncias d
LEFT JOIN departamentos dep ON d.departamento_id = dep.id
LEFT JOIN modalidades mod ON d.modalidad_id = mod.id
LIMIT 100;
```

### Módulos y Responsabilidades

| Módulo | Responsabilidad |
|--------|-----------------|
| `app.py` | Interfaz Streamlit, coordinar flujos |
| `database.py` | Conexión SQLite, CRUD, JOINs, consultas |
| `processing.py` | Carga, limpieza, filtrado, agregaciones |
| `download_data.py` | Descarga HTTP con reintentos, metadatos |
| `viz.py` | Gráficos Altair (barras, líneas, heatmaps) |
| `analysis.py` | Predicción, crecimiento, correlación |
| `utils.py` | Decoradores, logging centralizado |
| `exceptions.py` | Excepciones personalizadas |

### Decoradores Implementados

```python
@log_time(func)           # Mide tiempo de ejecución
@debug(func)              # Loguea args/kwargs/resultado
@cache_result(func)       # Cachea en sesión
@handle_errors(None)      # Captura excepciones sin propagar
```

---

## 📈 Análisis Incluidos

### Predicción (Regresión Lineal)
- Ajusta modelo lineal a tendencia histórica
- Predice N meses hacia adelante
- Visualiza datos + predicción en gráfico

### Crecimiento (YoY/Mensual)
- Calcula `pct_change()` acumulativo
- Retorna tasa de crecimiento (%)
- Análisis por año, mes o modalidad

### Correlación
- Crea matriz de pivot (dpto × modalidad)
- Calcula correlación de Pearson
- Visualiza como heatmap interactivo

---

## 🔒 Seguridad y Mejores Prácticas

✅ **SQL Injection**: Parámetros (`?`) en todas las consultas  
✅ **User-Agent**: Identificación responsable en descargas  
✅ **Reintentos**: Backoff exponencial (no spam)  
✅ **Caching**: Optimización de consultas repetidas  
✅ **Validación**: Tipificación exhaustiva de datos  
✅ **Logging**: Trazabilidad completa de operaciones  
✅ **Modularidad**: Separación clara de responsabilidades  

---

## 📝 Cumplimiento de Criterios 3.2 (60%)

| Criterio | Implementado | Ubicación |
|----------|-------------|-----------|
| **API/web scraping responsable** | ✅ | `download_data.py` (reintentos, metadatos) |
| **Persistencia (SQLite, 2+ tablas)** | ✅ | `database.py` (4 tablas con FK) |
| **Esquema y JOINs** | ✅ | `database.py` (create_schema, obtener_denuncias_join) |
| **Procesamiento/transformaciones** | ✅ | `processing.py` (clean, filter, agregaciones) |
| **Modelo simple (regresión)** | ✅ | `analysis.py` (predict_monthly_trend) |
| **Dashboard completo** | ✅ | `app.py` (6+ viz, 10+ controles) |
| **Visualizaciones interactivas** | ✅ | `viz.py` (Altair), `app.py` (tabs, gráficos) |
| **Múltiples controles** | ✅ | `app.py` (selectbox, multiselect, slider, checkbox) |
| **KPIs e indicadores** | ✅ | `app.py` (st.metric, growth, predicción) |
| **Manejo errores (try/except)** | ✅ | Todos los módulos |
| **Excepciones personalizadas** | ✅ | `exceptions.py` (6 clases) |
| **Decoradores** | ✅ | `utils.py` (4 decoradores aplicados) |
| **Logging/debug** | ✅ | `utils.py` (archivo + consola, DEBUG) |
| **Estructura modular** | ✅ | 8 módulos independientes |

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
```powershell
pip install -r requirements.txt
```

### Error: "No such table: denuncias"
- Haz clic en "💾 Cargar CSV a Base de Datos" en la app
- O ejecuta manualmente desde terminal

### Error: "requests.exceptions.ConnectionError"
- Verifica conexión a internet
- El app reintentará automáticamente (3 intentos)
- Revisa `logs/sidpol.log` para detalles

### Error: "FileNotFoundError" en CSV
- Primero descarga con "📥 Descargar/Actualizar CSV"
- O coloca manualmente un CSV en `data/`

---

## 📚 Documentación

- **Técnica detallada**: Ver `docs/ARCHITECTURE.md`
- **Logs**: `logs/sidpol.log` (DEBUG)
- **Consultas SQL**: Ejemplos en `database.py`

---

## 👨‍💻 Desarrollo

### Agregar una nueva visualización:
1. Crear función en `viz.py`
2. Llamar desde `app.py` en la sección correspondiente
3. Loguear en `utils.py`

### Agregar una nueva métrica:
1. Crear función en `analysis.py` con `@log_time`
2. Llamar desde `app.py` en pestañas
3. Usar try/except y logger

### Agregar un nuevo decorador:
1. Implementar en `utils.py`
2. Aplicar con `@nombre_decorador` en funciones críticas
3. Documentar en docstring

---

## 📞 Contacto y Soporte

- **Repo**: [GitHub](<repo_url>)
- **Issues**: Crear en GitHub
- **Email**: [si aplica]

---

## 📜 Licencia

Datos bajo **ODC-By** (atribución requerida)  
Código bajo [licencia del proyecto]

**Fuente**: SIDPOL/SIDPPOL – MININTER Perú (2018–2025)

---

**Última actualización**: Noviembre 2025  
**Estado**: ✅ Completo (Entrega 3.2)  
**Versión**: 1.0
