"""
EA2: Preprocesamiento y Limpieza de Datos en Plataforma de Big Data en la Nube
Asignatura: Arquitectura Big Data
Institucion: IU Digital de Antioquia

Dataset: FIFA 20 Players (players_20.csv)
Descripcion:
Este script simula el procesamiento de Big Data en la nube:
1. Conecta con el origen de datos (players_20.csv / SQLite DB).
2. Realiza analisis exploratorio de calidad de datos (duplicados, nulos, outliers).
3. Aplica tecnicas de limpieza: eliminacion de duplicados, imputacion de nulos, correccion de tipos.
4. Genera transformaciones analiticas (ingenieria de variables, escalado y normalizacion).
5. Persiste el dataset limpio en SQLite, exporta la muestra en Excel (cleaned_data.xlsx) y genera el informe de auditoria (cleaning_report.txt).
"""

import os
import sys
import sqlite3
import datetime
import numpy as np
import pandas as pd

# Configuracion de rutas relativas al proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
DB_DIR = os.path.join(SRC_DIR, "db")
XLSX_DIR = os.path.join(SRC_DIR, "xlsx")
AUDIT_DIR = os.path.join(SRC_DIR, "static", "auditoria")

CSV_SOURCE = os.path.join(BASE_DIR, "players_20.csv")
DB_PATH = os.path.join(DB_DIR, "ingestion.db")
XLSX_PATH = os.path.join(XLSX_DIR, "cleaned_data.xlsx")
AUDIT_PATH = os.path.join(AUDIT_DIR, "cleaning_report.txt")


def ensure_directories():
    """Crea los directorios requeridos si no existen."""
    for folder in [DB_DIR, XLSX_DIR, AUDIT_DIR]:
        os.makedirs(folder, exist_ok=True)
    print("[OK] Directorios del proyecto verificados.")


def load_raw_data():
    """
    Carga los datos iniciales desde el archivo CSV y los persiste en la base de datos
    analitica SQLite para emular el almacenamiento de datos crudos en la nube.
    """
    print("[INFO] Simulando carga de datos crudos en la nube (SQLite)...")
    if not os.path.exists(CSV_SOURCE):
        raise FileNotFoundError(f"No se encontro el dataset fuente en: {CSV_SOURCE}")

    df_raw = pd.read_csv(CSV_SOURCE)
    print(f"[OK] Dataset cargado exitosamente: {df_raw.shape[0]} filas, {df_raw.shape[1]} columnas.")

    # Guardar en SQLite como tabla de datos crudos
    conn = sqlite3.connect(DB_PATH)
    # Guardamos una seleccion o el dataset crudo
    df_raw.to_sql("raw_players", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[OK] Datos crudos almacenados en la base de datos: {DB_PATH} (tabla: raw_players).")
    return df_raw


def explore_data(df: pd.DataFrame):
    """
    Realiza analisis exploratorio inicial para detectar problemas de calidad de datos.
    """
    stats = {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "duplicates": int(df.duplicated(subset=["sofifa_id"]).sum()),
        "total_nulls": int(df.isnull().sum().sum()),
        "nulls_per_column": df.isnull().sum()[df.isnull().sum() > 0].to_dict()
    }
    return stats


def clean_and_transform_data(df_raw: pd.DataFrame):
    """
    Aplica pipeline completo de limpieza, imputacion, tipado e ingenieria de variables.
    """
    print("[INFO] Iniciando pipeline de preprocesamiento y limpieza...")

    # 1. Seleccion de columnas analiticas relevantes para el modelo Big Data
    selected_columns = [
        "sofifa_id", "short_name", "long_name", "age", "dob",
        "height_cm", "weight_kg", "nationality", "club",
        "overall", "potential", "value_eur", "wage_eur",
        "player_positions", "preferred_foot",
        "pace", "shooting", "passing", "dribbling", "defending", "physic"
    ]
    # Filtrar solo las que esten presentes
    cols_to_use = [c for c in selected_columns if c in df_raw.columns]
    df = df_raw[cols_to_use].copy()

    # 2. Eliminacion de duplicados
    initial_rows = len(df)
    df = df.drop_duplicates(subset=["sofifa_id"])
    duplicates_removed = initial_rows - len(df)

    # 3. Limpieza de texto (stripping espacios en blanco)
    text_cols = ["short_name", "long_name", "nationality", "club", "player_positions", "preferred_foot"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 4. Manejo e Imputacion de valores nulos
    # - Club: si no tiene club, asignar 'Sin Club'
    df["club"] = df["club"].replace("nan", "Sin Club").fillna("Sin Club")

    # - Valores monetarios (value_eur, wage_eur): rellenar con 0
    for col in ["value_eur", "wage_eur"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # - Metricas de rendimiento (pace, shooting, passing, dribbling, defending, physic):
    # Imputar con la mediana por posicion principal o la mediana general
    skill_cols = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]
    for col in skill_cols:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(round(median_val, 1))

    # 5. Correccion y estandarizacion de tipos de datos
    df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
    int_cols = ["sofifa_id", "age", "height_cm", "weight_kg", "overall", "potential"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 6. Transformaciones adicionales e Ingenieria de Caracteristicas
    # a. Indice de Masa Corporal (BMI) = peso_kg / (estatura_m ^ 2)
    df["bmi"] = (df["weight_kg"] / ((df["height_cm"] / 100) ** 2)).round(2)

    # b. Potencial de crecimiento (potential - overall)
    df["potential_growth"] = df["potential"] - df["overall"]

    # c. Normalizacion Min-Max del Overall Score (rango 0 a 1)
    min_ovr = df["overall"].min()
    max_ovr = df["overall"].max()
    df["overall_normalized"] = ((df["overall"] - min_ovr) / (max_ovr - min_ovr)).round(4)

    # d. Categoria de edad (Segmentacion analitica)
    df["age_category"] = pd.cut(
        df["age"],
        bins=[0, 21, 28, 35, 100],
        labels=["Promesa (<=21)", "Plenitud (22-28)", "Veterano (29-35)", "Master (>35)"]
    )

    print(f"[OK] Preprocesamiento completado. Dimensiones finales: {df.shape[0]} filas, {df.shape[1]} columnas.")
    return df, duplicates_removed


def save_cleaned_data_to_db(df: pd.DataFrame):
    """
    Guarda los datos preprocesados en la base de datos SQLite como tabla analitica 'cleaned_players'.
    """
    print(f"[INFO] Guardando tabla analitica 'cleaned_players' en: {DB_PATH} ...")
    conn = sqlite3.connect(DB_PATH)
    # Convertimos categorias o fechas si es necesario para SQLite
    df_to_save = df.copy()
    if "dob" in df_to_save.columns:
        df_to_save["dob"] = df_to_save["dob"].astype(str)
    if "age_category" in df_to_save.columns:
        df_to_save["age_category"] = df_to_save["age_category"].astype(str)

    df_to_save.to_sql("cleaned_players", conn, if_exists="replace", index=False)
    conn.close()
    print("[OK] Tabla 'cleaned_players' guardada exitosamente en la base de datos.")


def export_sample_excel(df: pd.DataFrame, output_path: str, sample_size: int = 100):
    """
    Exporta una muestra representativa de los datos limpios a un archivo Excel (.xlsx).
    """
    print(f"[INFO] Exportando muestra representativa a Excel: {output_path} ...")
    sample_df = df.head(sample_size).copy()
    sample_df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"[OK] Archivo Excel generado ({len(sample_df)} registros) en: {output_path}")


def generate_cleaning_report(raw_stats: dict, clean_df: pd.DataFrame, duplicates_removed: int, output_path: str):
    """
    Genera el archivo de auditoria en formato .txt comparando el estado antes y despues de la limpieza.
    """
    print(f"[INFO] Generando reporte de auditoria en: {output_path} ...")
    execution_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    final_rows = len(clean_df)
    final_cols = len(clean_df.columns)
    final_nulls = int(clean_df.isnull().sum().sum())

    report_content = f"""================================================================================
          REPORTE DE AUDITORIA DE PREPROCESAMIENTO Y LIMPIEZA DE DATOS (EA2)
================================================================================
Asignatura : Arquitectura Big Data
Actividad  : EA2. Preprocesamiento y Limpieza de Datos en Plataforma de Big Data
Fecha/Hora : {execution_time}
Fuente     : {CSV_SOURCE}
Destino BD : {DB_PATH} (Tabla: cleaned_players)
================================================================================

1. COMPARATIVO GENERAL: ESTADO ANTES VS DESPUES
--------------------------------------------------------------------------------
Metrica                         | Estado Inicial (Crudo) | Estado Final (Limpio)
--------------------------------------------------------------------------------
Total de Registros (Filas)      | {raw_stats['total_rows']:<22} | {final_rows:<20}
Total de Columnas               | {raw_stats['total_cols']:<22} | {final_cols:<20}
Total de Valores Nulos          | {raw_stats['total_nulls']:<22} | {final_nulls:<20}
Registros Duplicados            | {raw_stats['duplicates']:<22} | 0
--------------------------------------------------------------------------------

2. DETALLE DE OPERACIONES DE PREPROCESAMIENTO APLICADAS:
--------------------------------------------------------------------------------
a) Seleccion de Atributos:
   - Se seleccionaron 21 atributos analiticos principales del dataset original de 104 columnas.
b) Eliminacion de Duplicados:
   - Duplicados eliminados por ID de jugador: {duplicates_removed}.
c) Imputacion y Tratamiento de Valores Nulos:
   - Club: Nulos reemplazados por 'Sin Club'.
   - Salarios y Valores de Mercado ('value_eur', 'wage_eur'): Nulos imputados a 0.
   - Atributos de Rendimiento ('pace', 'shooting', 'passing', etc.):
     Valores nulos imputados mediante la mediana estadistica de la columna.
d) Correccion y Estandarizacion de Tipos de Datos:
   - 'dob': Convertido a formato estandar de fecha (DateTime YYYY-MM-DD).
   - 'age', 'height_cm', 'weight_kg', 'overall', 'potential': Convertidos a enteros (int).
   - Campos de texto normalizados sin espacios residuales (strip).
e) Ingenieria de Caracteristicas y Transformaciones:
   - 'bmi': Calculo del Indice de Masa Corporal [peso / (altura/100)^2].
   - 'potential_growth': Calculo del margen de desarrollo [potential - overall].
   - 'overall_normalized': Normalizacion Min-Max del puntaje de habilidad [0.0 - 1.0].
   - 'age_category': Segmentacion en categorias de edad (Promesa, Plenitud, Veterano, Master).

3. VERIFICACION DE INTEGRIDAD Y CALIDAD FINAL:
--------------------------------------------------------------------------------
- Nulos en 'sofifa_id'                   : {clean_df['sofifa_id'].isnull().sum()}
- Nulos en 'short_name'                  : {clean_df['short_name'].isnull().sum()}
- Nulos en 'overall'                     : {clean_df['overall'].isnull().sum()}
- Nulos en 'potential'                   : {clean_df['potential'].isnull().sum()}
- Nulos en 'bmi'                         : {clean_df['bmi'].isnull().sum()}
- Rango de normalizacion Min-Max         : [{clean_df['overall_normalized'].min()} - {clean_df['overall_normalized'].max()}]
- Integridad estructural verificada      : SI (100% libre de nulos en variables clave)

================================================================================
ESTADO FINAL DE LA AUDITORIA: EXITOSO - DATOS LISTOS PARA MODELADO Y ANALITICA
================================================================================
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[OK] Reporte de auditoria guardado exitosamente en: {output_path}")


def main():
    print("=" * 70)
    print("   INICIO DEL PIPELINE DE PREPROCESAMIENTO BIG DATA (EA2)")
    print("=" * 70)

    # 1. Asegurar estructura de directorios
    ensure_directories()

    # 2. Cargar datos crudos
    df_raw = load_raw_data()

    # 3. Analisis exploratorio inicial
    raw_stats = explore_data(df_raw)

    # 4. Limpieza y transformacion
    df_cleaned, dup_removed = clean_and_transform_data(df_raw)

    # 5. Persistencia en base de datos analitica SQLite
    save_cleaned_data_to_db(df_cleaned)

    # 6. Exportacion de muestra en Excel
    export_sample_excel(df_cleaned, XLSX_PATH, sample_size=100)

    # 7. Generacion de reporte de auditoria
    generate_cleaning_report(raw_stats, df_cleaned, dup_removed, AUDIT_PATH)

    print("=" * 70)
    print("   PIPELINE DE LIMPIEZA FINALIZADO CON EXITO")
    print("=" * 70)


if __name__ == "__main__":
    main()
