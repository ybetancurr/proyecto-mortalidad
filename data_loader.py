"""
data_loader.py
==============
Carga, limpieza y preparación de datos para el dashboard de mortalidad Colombia 2019.
Produce un DataFrame base y funciones que retornan los datos listos para cada gráfico.
"""

import pandas as pd
import os

# ── Rutas ──────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

NOFETAL_PATH   = os.path.join(DATA_DIR, "Anexo1.NoFetal2019_CE_15-03-23.xlsx")
CODIGOS_PATH   = os.path.join(DATA_DIR, "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx")
DIVIPOLA_PATH  = os.path.join(DATA_DIR, "Divipola_CE_.xlsx")

# ── Diccionarios fijos ─────────────────────────────────────────────────────────
SEXO_MAP = {1: "Hombre", 2: "Mujer"}

MESES_MAP = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

# Mapeo GRUPO_EDAD1 → categoría de ciclo de vida (tabla del enunciado)
EDAD_MAP = {
    0:  "Mortalidad neonatal",
    1:  "Mortalidad neonatal",
    2:  "Mortalidad neonatal",
    3:  "Mortalidad neonatal",
    4:  "Mortalidad neonatal",
    5:  "Mortalidad infantil",
    6:  "Mortalidad infantil",
    7:  "Primera infancia",
    8:  "Primera infancia",
    9:  "Niñez",
    10: "Niñez",
    11: "Adolescencia",
    12: "Juventud",
    13: "Juventud",
    14: "Adultez temprana",
    15: "Adultez temprana",
    16: "Adultez temprana",
    17: "Adultez intermedia",
    18: "Adultez intermedia",
    19: "Adultez intermedia",
    20: "Vejez",
    21: "Vejez",
    22: "Vejez",
    23: "Vejez",
    24: "Vejez",
    25: "Longevidad / Centenarios",
    26: "Longevidad / Centenarios",
    27: "Longevidad / Centenarios",
    28: "Longevidad / Centenarios",
    29: "Edad desconocida",
}

# Orden para el eje X del histograma
EDAD_ORDEN = [
    "Mortalidad neonatal",
    "Mortalidad infantil",
    "Primera infancia",
    "Niñez",
    "Adolescencia",
    "Juventud",
    "Adultez temprana",
    "Adultez intermedia",
    "Vejez",
    "Longevidad / Centenarios",
    "Edad desconocida",
]


# ══════════════════════════════════════════════════════════════════════════════
# 1. CARGA BASE
# ══════════════════════════════════════════════════════════════════════════════

def _cargar_divipola() -> pd.DataFrame:
    """Carga Divipola y normaliza tipos."""
    df = pd.read_excel(DIVIPOLA_PATH, dtype=str)
    df.columns = df.columns.str.strip()
    # Convertir códigos a int para que el merge sea limpio
    df["COD_DEPARTAMENTO"] = pd.to_numeric(df["COD_DEPARTAMENTO"], errors="coerce")
    df["COD_MUNICIPIO"]    = pd.to_numeric(df["COD_MUNICIPIO"],    errors="coerce")
    df["DEPARTAMENTO"] = df["DEPARTAMENTO"].str.strip().str.title()
    df["MUNICIPIO"]    = df["MUNICIPIO"].str.strip().str.title()
    return df[["COD_DEPARTAMENTO", "COD_MUNICIPIO", "DEPARTAMENTO", "MUNICIPIO"]].drop_duplicates()


def _cargar_codigos() -> pd.DataFrame:
    """Carga el catálogo de causas de muerte a 4 caracteres."""
    df = pd.read_excel(CODIGOS_PATH, dtype=str)
    df.columns = df.columns.str.strip()
    # Renombrar para trabajar cómodamente
    df = df.rename(columns={
        "Código de la CIE-10 cuatro caracteres":              "COD_MUERTE",
        "Descripcion  de códigos mortalidad a cuatro caracteres": "NOMBRE_CAUSA",
    })
    df["COD_MUERTE"]    = df["COD_MUERTE"].str.strip().str.upper()
    df["NOMBRE_CAUSA"]  = df["NOMBRE_CAUSA"].str.strip()
    return df[["COD_MUERTE", "NOMBRE_CAUSA"]].drop_duplicates()


def _cargar_nofetal() -> pd.DataFrame:
    """Carga el archivo principal de muertes y aplica limpieza básica."""
    df = pd.read_excel(NOFETAL_PATH)
    df.columns = df.columns.str.strip()

    # Tipos numéricos
    for col in ["COD_DEPARTAMENTO", "COD_MUNICIPIO", "MES", "SEXO", "GRUPO_EDAD1"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalizar código de muerte
    df["COD_MUERTE"] = df["COD_MUERTE"].astype(str).str.strip().str.upper()

    return df


def cargar_datos() -> dict:
    """
    Punto de entrada principal.
    Retorna un dict con todos los DataFrames necesarios para las visualizaciones.
    Llama esta función UNA sola vez al iniciar la app y pasa el dict a cada figura.
    """
    divipola = _cargar_divipola()
    codigos  = _cargar_codigos()
    nofetal  = _cargar_nofetal()

    # ── DataFrame enriquecido (base para casi todos los gráficos) ────────────
    base = (
        nofetal
        .merge(divipola, on=["COD_DEPARTAMENTO", "COD_MUNICIPIO"], how="left")
        .merge(codigos,  on="COD_MUERTE",                           how="left")
    )

    base["SEXO_NOMBRE"]    = base["SEXO"].map(SEXO_MAP).fillna("Sin información")
    base["MES_NOMBRE"]     = base["MES"].map(MESES_MAP)
    base["CATEGORIA_EDAD"] = base["GRUPO_EDAD1"].map(EDAD_MAP).fillna("Edad desconocida")

    return {
        "base":     base,
        "divipola": divipola,
        "codigos":  codigos,
    }


# ══════════════════════════════════════════════════════════════════════════════
# 2. FUNCIONES POR GRÁFICO
# ══════════════════════════════════════════════════════════════════════════════

def get_muertes_por_departamento(datos: dict) -> pd.DataFrame:
    """
    Gráfico 1 — Mapa.
    Retorna: COD_DEPARTAMENTO | DEPARTAMENTO | TOTAL_MUERTES
    """
    base = datos["base"]
    df = (
        base.groupby(["COD_DEPARTAMENTO", "DEPARTAMENTO"])
        .size()
        .reset_index(name="TOTAL_MUERTES")
        .dropna(subset=["DEPARTAMENTO"])
        .sort_values("TOTAL_MUERTES", ascending=False)
    )
    return df


def get_muertes_por_mes(datos: dict) -> pd.DataFrame:
    """
    Gráfico 2 — Líneas.
    Retorna: MES | MES_NOMBRE | TOTAL_MUERTES
    """
    base = datos["base"]
    df = (
        base.groupby(["MES", "MES_NOMBRE"])
        .size()
        .reset_index(name="TOTAL_MUERTES")
        .dropna(subset=["MES"])
        .sort_values("MES")
    )
    return df


def get_ciudades_mas_violentas(datos: dict, top_n: int = 5) -> pd.DataFrame:
    """
    Gráfico 3 — Barras homicidios.
    Filtra códigos X95x (agresión con disparo de arma de fuego).
    Retorna: MUNICIPIO | TOTAL_HOMICIDIOS  (top_n filas)
    """
    base = datos["base"]
    homicidios = base[base["COD_MUERTE"].str.startswith("X95", na=False)]
    df = (
        homicidios.groupby("MUNICIPIO")
        .size()
        .reset_index(name="TOTAL_HOMICIDIOS")
        .dropna(subset=["MUNICIPIO"])
        .sort_values("TOTAL_HOMICIDIOS", ascending=False)
        .head(top_n)
    )
    return df


def get_ciudades_menor_mortalidad(datos: dict, bottom_n: int = 10) -> pd.DataFrame:
    """
    Gráfico 4 — Pie chart.
    Retorna: MUNICIPIO | TOTAL_MUERTES  (bottom_n ciudades con menos muertes)
    """
    base = datos["base"]
    df = (
        base.groupby("MUNICIPIO")
        .size()
        .reset_index(name="TOTAL_MUERTES")
        .dropna(subset=["MUNICIPIO"])
        .sort_values("TOTAL_MUERTES", ascending=True)
        .head(bottom_n)
    )
    return df


def get_top_causas(datos: dict, top_n: int = 10) -> pd.DataFrame:
    """
    Gráfico 5 — Tabla.
    Retorna: COD_MUERTE | NOMBRE_CAUSA | TOTAL_CASOS  (top_n causas)
    """
    base = datos["base"]
    df = (
        base.groupby(["COD_MUERTE", "NOMBRE_CAUSA"])
        .size()
        .reset_index(name="TOTAL_CASOS")
        .dropna(subset=["NOMBRE_CAUSA"])
        .sort_values("TOTAL_CASOS", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return df


def get_muertes_por_sexo_departamento(datos: dict) -> pd.DataFrame:
    """
    Gráfico 6 — Barras apiladas.
    Retorna: DEPARTAMENTO | SEXO_NOMBRE | TOTAL_MUERTES
    """
    base = datos["base"]
    df = (
        base.groupby(["DEPARTAMENTO", "SEXO_NOMBRE"])
        .size()
        .reset_index(name="TOTAL_MUERTES")
        .dropna(subset=["DEPARTAMENTO"])
        .sort_values(["DEPARTAMENTO", "SEXO_NOMBRE"])
    )
    return df


def get_distribucion_edad(datos: dict) -> pd.DataFrame:
    """
    Gráfico 7 — Histograma por ciclo de vida.
    Retorna: CATEGORIA_EDAD | TOTAL_MUERTES  (en orden de ciclo de vida)
    """
    base = datos["base"]
    df = (
        base.groupby("CATEGORIA_EDAD")
        .size()
        .reset_index(name="TOTAL_MUERTES")
    )
    # Aplicar orden correcto del ciclo de vida
    df["CATEGORIA_EDAD"] = pd.Categorical(
        df["CATEGORIA_EDAD"], categories=EDAD_ORDEN, ordered=True
    )
    df = df.sort_values("CATEGORIA_EDAD").reset_index(drop=True)
    return df