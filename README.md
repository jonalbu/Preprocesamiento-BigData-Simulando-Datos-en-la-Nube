# EA2: Preprocesamiento y Limpieza de Datos en Plataforma de Big Data en la Nube

**Institución Universitaria Digital de Antioquia (IU Digital)**  
**Programa:** Ingeniería en Software / Tecnología en Desarrollo de Software  
**Asignatura:** Arquitectura Big Data (7° Semestre)  
**Actividad:** EA2. Preprocesamiento y Limpieza de Datos en Plataforma de Big Data en la Nube  
**Dataset Utilizado:** FIFA 20 Complete Player Dataset (`players_20.csv` - 18,278 registros)  
**Estudiante:** Jonathan Alvarez Bustamante

---

## 1. Descripción de la Solución

Esta actividad implementa la segunda fase fundamental del ciclo de vida de Big Data: **Preprocesamiento, Depuración y Limpieza de Datos** en un entorno que simula almacenamiento y procesamiento distribuido en la nube.

### Flujo del Pipeline de Datos:
1. **Carga y Simulación Cloud:** Conexión con el dataset `players_20.csv` (18,278 filas y 104 columnas) y persistencia del estado crudo en la base de datos analítica SQLite `src/db/ingestion.db` (tabla `raw_players`), emulando un servicio de almacenamiento Data Lake en la nube (S3 / Blob Storage).
2. **Análisis Exploratorio de Calidad (EDA):** Identificación automática de registros duplicados, tipos de datos inconsistentes y más de 240,000 valores nulos en el conjunto original.
3. **Limpieza y Depuración:**
   - **Selección de Variables Clave:** Reducción dimensional a 21 columnas analíticas de alto impacto.
   - **Eliminación de Duplicados:** Validación de unicidad sobre la clave primaria `sofifa_id`.
   - **Imputación Estratégica de Nulos:**
     - Valores monetarios (`value_eur`, `wage_eur`): Imputación con `0`.
     - Pertenencia a clubes (`club`): Sustitución de nulos por `'Sin Club'`.
     - Métricas técnicas y físicas (`pace`, `shooting`, `passing`, `dribbling`, `defending`, `physic`): Imputación estadística mediante la **mediana** de cada atributo.
   - **Corrección de Tipos de Datos:** Conversión de fechas (`dob`) a `datetime` (YYYY-MM-DD), campos métricos y edades a enteros (`int`), y limpieza de cadenas de texto (`strip`).
4. **Ingeniería de Características y Transformaciones:**
   - **Índice de Masa Corporal (`bmi`):** Cálculo biométrico $\text{peso\_kg} / (\text{altura\_m})^2$.
   - **Potencial de Crecimiento (`potential_growth`):** Margen de mejora $\text{potential} - \text{overall}$.
   - **Normalización Min-Max (`overall_normalized`):** Escalado del puntaje general al rango $[0.0, 1.0]$.
   - **Segmentación por Edad (`age_category`):** Categorización analítica en *Promesa*, *Plenitud*, *Veterano* y *Master*.
5. **Almacenamiento y Evidencias:**
   - Guardado de la tabla limpia final `cleaned_players` en SQLite (`src/db/ingestion.db`).
   - Generación del archivo Excel [`src/xlsx/cleaned_data.xlsx`](src/xlsx/cleaned_data.xlsx) con una muestra representativa.
   - Generación del informe de auditoría [`src/static/auditoria/cleaning_report.txt`](src/static/auditoria/cleaning_report.txt) que detalla el estado **ANTES vs DESPUÉS**.
6. **Automatización CI/CD con GitHub Actions:** Workflow en [`.github/workflows/bigdata.yml`](.github/workflows/bigdata.yml) que ejecuta el pipeline completo y publica los artefactos generados.

---

## 2. Estructura del Proyecto

El proyecto cumple estrictamente con el estándar exigido en la guía de la actividad:

```text
Tarea_2/
├── players_20.csv                    <- Dataset fuente (FIFA 20 Players)
├── setup.py                          <- Empaquetado del proyecto
├── requirements.txt                  <- Dependencias del entorno
├── README.md                         <- Documentacion y trazabilidad
├── .gitignore                        <- Exclusiones de Git
├── .github/
│   └── workflows/
│       └── bigdata.yml               <- Pipeline de GitHub Actions
└── src/
    ├── cleaning.py                   <- Script de preprocesamiento y limpieza
    ├── db/
    │   └── ingestion.db              <- Base de datos SQLite (tablas raw y cleaned)
    ├── xlsx/
    │   └── cleaned_data.xlsx         <- Muestra representativa de datos limpios
    └── static/
        └── auditoria/
            └── cleaning_report.txt   <- Reporte comparativo de auditoria
```

---

## 3. Instrucciones de Ejecución Local

### Prerrequisitos
- Python 3.9 o superior.
- Git.

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

### Paso 2: Crear y activar entorno virtual
- **En Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar el pipeline de limpieza
```bash
python src/cleaning.py
```

---

## 4. Automatización con GitHub Actions

El archivo [`.github/workflows/bigdata.yml`](.github/workflows/bigdata.yml) automatiza:
1. Configuración del entorno **Python 3.11**.
2. Instalación de librerías (`pandas`, `openpyxl`, `numpy`, `scikit-learn`).
3. Ejecución de `python src/cleaning.py`.
4. Comprobación mediante aserciones (`test -f`) de la generación de la BD, Excel y reporte TXT.
5. Impresión en consola del reporte de auditoría completo.
6. Empaquetado y subida de artefactos (`preprocessing-evidences`) para descarga directa desde GitHub.

---

## 5. Reporte de Auditoría de Limpieza (Resumen)

| Métrica | Estado Inicial (Crudo) | Estado Final (Limpio) |
| :--- | :---: | :---: |
| **Total Registros** | 18,278 | 18,278 |
| **Total Columnas** | 104 | 25 |
| **Total Valores Nulos** | 244,935 | **0** (100% Imputados / Limpios) |
| **Registros Duplicados** | 0 | 0 |
| **Nuevas Variables Analíticas** | 0 | 4 (`bmi`, `potential_growth`, `overall_normalized`, `age_category`) |
| **Estado Final** | Datos Crudos | **EXITOSO - Datos listos para modelado** |
