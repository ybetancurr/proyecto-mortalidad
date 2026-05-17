"""
figures.py
==========
Una función por gráfico. Cada función recibe el dict de datos de data_loader
y retorna una figura Plotly lista para incrustar en Dash.
"""

import plotly.express as px
import plotly.graph_objects as go
import json
import os
import requests

from data_loader import EDAD_ORDEN

# ── Paleta y estilos globales ──────────────────────────────────────────────────
COLOR_PRIMARY   = "#C0392B"   # rojo Colombia
COLOR_SECONDARY = "#2C3E50"   # azul oscuro
COLOR_ACCENT    = "#F39C12"   # amarillo Colombia
COLOR_BG        = "#F8F9FA"

COLORES_SEXO = {
    "Hombre":          COLOR_SECONDARY,
    "Mujer":           COLOR_PRIMARY,
    "Sin información": "#95A5A6",
}

TEMPLATE = "plotly_white"

TITULO_FONT = dict(size=15, color=COLOR_SECONDARY, family="Georgia, serif")
AXIS_FONT   = dict(size=11, color="#555")

def _base_layout(titulo: str) -> dict:
    """Layout base reutilizable para todas las figuras."""
    return dict(
        title=dict(text=titulo, font=TITULO_FONT, x=0.5, xanchor="center"),
        plot_bgcolor=COLOR_BG,
        paper_bgcolor="white",
        font=dict(family="Segoe UI, sans-serif", size=11, color="#333"),
        margin=dict(l=50, r=30, t=60, b=50),
        legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#DDD", borderwidth=1),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1. MAPA — Muertes por departamento
# ══════════════════════════════════════════════════════════════════════════════

def _cargar_geojson() -> dict:
    """
    Intenta cargar el GeoJSON local; si no existe, lo descarga de GitHub.
    El archivo debe tener la propiedad 'DPTO' con el código numérico del dpto.
    """
    local_path = os.path.join(os.path.dirname(__file__), "data", "colombia_departamentos.geojson")
    if os.path.exists(local_path):
        with open(local_path, encoding="utf-8") as f:
            return json.load(f)

    # Fuente pública con geometrías DANE
    url = (
        "https://raw.githubusercontent.com/deldersveld/topojson/master/"
        "countries/colombia/colombia-departments.json"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def fig_mapa(datos: dict) -> go.Figure:
    """
    Mapa coroplético: total de muertes por departamento.
    Usa Plotly Express choropleth_mapbox con GeoJSON de Colombia.
    """
    from data_loader import get_muertes_por_departamento
    df = get_muertes_por_departamento(datos)

    geojson = _cargar_geojson()

    if geojson is None:
        # Fallback: gráfico de barras horizontal si no hay GeoJSON disponible
        fig = px.bar(
            df.sort_values("TOTAL_MUERTES"),
            x="TOTAL_MUERTES", y="DEPARTAMENTO",
            orientation="h",
            color="TOTAL_MUERTES",
            color_continuous_scale="Reds",
            labels={"TOTAL_MUERTES": "Total muertes", "DEPARTAMENTO": "Departamento"},
        )
        fig.update_layout(**_base_layout("Muertes por departamento — Colombia 2019 (sin mapa)"))
        return fig

    # Detectar la propiedad de código en el GeoJSON
    # El GeoJSON de deldersveld usa 'DPTO' como código de departamento (string con ceros)
    df["COD_STR"] = df["COD_DEPARTAMENTO"].astype(int).astype(str).str.zfill(2)

    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="COD_STR",
        featureidkey="properties.DPTO",
        color="TOTAL_MUERTES",
        color_continuous_scale="Reds",
        mapbox_style="carto-positron",
        zoom=4.5,
        center={"lat": 4.5, "lon": -74.0},
        opacity=0.75,
        hover_name="DEPARTAMENTO",
        hover_data={"TOTAL_MUERTES": True, "COD_STR": False},
        labels={"TOTAL_MUERTES": "Total muertes"},
    )
    fig.update_layout(
        **_base_layout("Distribución de muertes por departamento — Colombia 2019"),
        margin=dict(l=0, r=0, t=60, b=0),
        height=520,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 2. LÍNEAS — Muertes por mes
# ══════════════════════════════════════════════════════════════════════════════

def fig_lineas_mes(datos: dict) -> go.Figure:
    """Gráfico de líneas: total de muertes por mes."""
    from data_loader import get_muertes_por_mes
    df = get_muertes_por_mes(datos)

    fig = px.line(
        df,
        x="MES_NOMBRE", y="TOTAL_MUERTES",
        markers=True,
        labels={"MES_NOMBRE": "Mes", "TOTAL_MUERTES": "Total de muertes"},
        color_discrete_sequence=[COLOR_PRIMARY],
    )
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=8, color=COLOR_ACCENT, line=dict(width=1.5, color=COLOR_PRIMARY)),
    )
    fig.update_layout(
        **_base_layout("Total de muertes por mes — Colombia 2019"),
        xaxis=dict(tickfont=AXIS_FONT, title_font=AXIS_FONT),
        yaxis=dict(tickfont=AXIS_FONT, title_font=AXIS_FONT, gridcolor="#E5E5E5"),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 3. BARRAS — 5 ciudades más violentas (homicidios X95)
# ══════════════════════════════════════════════════════════════════════════════

def fig_barras_homicidios(datos: dict) -> go.Figure:
    """Barras verticales: top 5 municipios con más homicidios por arma de fuego (X95x)."""
    from data_loader import get_ciudades_mas_violentas
    df = get_ciudades_mas_violentas(datos, top_n=5)

    fig = px.bar(
        df,
        x="MUNICIPIO", y="TOTAL_HOMICIDIOS",
        text="TOTAL_HOMICIDIOS",
        color="TOTAL_HOMICIDIOS",
        color_continuous_scale=[[0, "#FADBD8"], [1, COLOR_PRIMARY]],
        labels={"MUNICIPIO": "Ciudad", "TOTAL_HOMICIDIOS": "Homicidios (X95)"},
    )
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        **_base_layout("5 ciudades más violentas — Homicidios con arma de fuego (X95) 2019"),
        xaxis=dict(tickfont=AXIS_FONT),
        yaxis=dict(tickfont=AXIS_FONT, gridcolor="#E5E5E5"),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 4. PIE — 10 ciudades con menor mortalidad
# ══════════════════════════════════════════════════════════════════════════════

def fig_pie_menor_mortalidad(datos: dict) -> go.Figure:
    """Gráfico circular: 10 municipios con menor cantidad de muertes."""
    from data_loader import get_ciudades_menor_mortalidad
    df = get_ciudades_menor_mortalidad(datos, bottom_n=10)

    fig = px.pie(
        df,
        names="MUNICIPIO",
        values="TOTAL_MUERTES",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.35,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        insidetextorientation="radial",
        hovertemplate="<b>%{label}</b><br>Muertes: %{value}<extra></extra>",
    )
    fig.update_layout(
        **_base_layout("10 municipios con menor índice de mortalidad — Colombia 2019"),
        showlegend=True,
    )
    fig.update_layout(legend=dict(orientation="v", x=1.02, y=0.5))
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 5. TABLA — Top 10 causas de muerte
# ══════════════════════════════════════════════════════════════════════════════

def tabla_top_causas(datos: dict) -> dict:
    """
    Retorna columnas y datos listos para dash_table.DataTable.
    No devuelve una figura Plotly sino un dict compatible con Dash.
    """
    from data_loader import get_top_causas
    df = get_top_causas(datos, top_n=10)
    df = df.rename(columns={
        "COD_MUERTE":   "Código",
        "NOMBRE_CAUSA": "Causa de muerte",
        "TOTAL_CASOS":  "Total de casos",
    })

    columns = [{"name": col, "id": col} for col in df.columns]
    records = df.to_dict("records")
    return {"columns": columns, "data": records}


# ══════════════════════════════════════════════════════════════════════════════
# 6. BARRAS APILADAS — Muertes por sexo y departamento
# ══════════════════════════════════════════════════════════════════════════════

def fig_barras_apiladas_sexo(datos: dict) -> go.Figure:
    """Barras apiladas: total de muertes por sexo en cada departamento."""
    from data_loader import get_muertes_por_sexo_departamento
    df = get_muertes_por_sexo_departamento(datos)

    fig = px.bar(
        df,
        x="DEPARTAMENTO", y="TOTAL_MUERTES",
        color="SEXO_NOMBRE",
        barmode="stack",
        color_discrete_map=COLORES_SEXO,
        labels={
            "DEPARTAMENTO":  "Departamento",
            "TOTAL_MUERTES": "Total de muertes",
            "SEXO_NOMBRE":   "Sexo",
        },
    )
    fig.update_layout(
        **_base_layout("Muertes por sexo en cada departamento — Colombia 2019"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=9), title_font=AXIS_FONT),
        yaxis=dict(tickfont=AXIS_FONT, gridcolor="#E5E5E5"),
        height=480,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 7. HISTOGRAMA — Distribución por ciclo de vida
# ══════════════════════════════════════════════════════════════════════════════

def fig_histograma_edad(datos: dict) -> go.Figure:
    """
    Barras ordenadas por ciclo de vida: muertes agrupadas por CATEGORIA_EDAD.
    Técnicamente es un gráfico de barras categórico ordenado (como pide el enunciado).
    """
    from data_loader import get_distribucion_edad
    df = get_distribucion_edad(datos)

    fig = px.bar(
        df,
        x="CATEGORIA_EDAD", y="TOTAL_MUERTES",
        text="TOTAL_MUERTES",
        color="TOTAL_MUERTES",
        color_continuous_scale=[[0, "#D6EAF8"], [1, COLOR_SECONDARY]],
        labels={"CATEGORIA_EDAD": "Grupo etario", "TOTAL_MUERTES": "Total de muertes"},
        category_orders={"CATEGORIA_EDAD": EDAD_ORDEN},
    )
    fig.update_traces(textposition="outside", textfont_size=10)
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        **_base_layout("Distribución de muertes por ciclo de vida — Colombia 2019"),
        xaxis=dict(tickangle=-30, tickfont=dict(size=10), title_font=AXIS_FONT),
        yaxis=dict(tickfont=AXIS_FONT, gridcolor="#E5E5E5"),
        height=460,
    )
    return fig