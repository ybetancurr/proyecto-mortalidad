"""
app.py
======
Punto de entrada de la aplicación Dash.
Carga los datos una sola vez al iniciar y construye el layout completo.
"""

import dash
from dash import html, dcc, dash_table

from data_loader import cargar_datos
from figures import (
    fig_mapa,
    fig_lineas_mes,
    fig_barras_homicidios,
    fig_pie_menor_mortalidad,
    fig_barras_apiladas_sexo,
    fig_histograma_edad,
    tabla_top_causas,
)

# ── Inicialización ─────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="Mortalidad Colombia 2019")
server = app.server  # necesario para gunicorn en Render

# Carga única de datos al arrancar la app
datos = cargar_datos()

# Figuras (calculadas una sola vez)
mapa             = fig_mapa(datos)
lineas           = fig_lineas_mes(datos)
barras_homicidio = fig_barras_homicidios(datos)
pie_menor        = fig_pie_menor_mortalidad(datos)
barras_sexo      = fig_barras_apiladas_sexo(datos)
histograma       = fig_histograma_edad(datos)
tabla            = tabla_top_causas(datos)


# ── Estilos inline reutilizables ───────────────────────────────────────────────
CARD = {
    "backgroundColor": "white",
    "borderRadius": "8px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
    "padding": "16px",
    "marginBottom": "20px",
}

HEADER_STYLE = {
    "backgroundColor": "#2C3E50",
    "color": "white",
    "padding": "28px 40px 20px",
    "marginBottom": "24px",
    "borderBottom": "4px solid #C0392B",
}

PAGE = {
    "backgroundColor": "#F0F2F5",
    "minHeight": "100vh",
    "fontFamily": "Segoe UI, sans-serif",
    "padding": "0 0 40px",
}

ROW = {
    "display": "grid",
    "gridTemplateColumns": "1fr 1fr",
    "gap": "20px",
    "padding": "0 32px",
    "marginBottom": "0",
}

FULL = {
    "padding": "0 32px",
}

SECTION_TITLE = {
    "fontSize": "12px",
    "fontWeight": "600",
    "letterSpacing": "1.5px",
    "textTransform": "uppercase",
    "color": "#C0392B",
    "marginBottom": "10px",
}

TABLE_HEADER = {
    "backgroundColor": "#2C3E50",
    "color": "white",
    "fontWeight": "bold",
    "fontSize": "13px",
    "textAlign": "left",
    "padding": "10px 14px",
}

TABLE_CELL = {
    "textAlign": "left",
    "fontSize": "13px",
    "padding": "9px 14px",
    "borderBottom": "1px solid #EEE",
    "whiteSpace": "normal",
    "height": "auto",
}


# ── Layout ─────────────────────────────────────────────────────────────────────
app.layout = html.Div(style=PAGE, children=[

    # ── Encabezado ──────────────────────────────────────────────────────────
    html.Div(style=HEADER_STYLE, children=[
        html.H1("Mortalidad en Colombia 2019",
                style={"margin": "0 0 6px", "fontSize": "26px", "fontWeight": "700"}),
        html.P("Análisis interactivo de datos de mortalidad no fetal · Fuente: DANE",
               style={"margin": 0, "fontSize": "13px", "color": "#BDC3C7"}),
    ]),

    # ── Fila 1: Mapa (ancho completo) ────────────────────────────────────────
    html.Div(style=FULL, children=[
        html.Div(style=CARD, children=[
            html.P("Distribución geográfica", style=SECTION_TITLE),
            dcc.Graph(figure=mapa, config={"displayModeBar": False}),
        ]),
    ]),

    # ── Fila 2: Líneas | Barras homicidios ───────────────────────────────────
    html.Div(style=ROW, children=[
        html.Div(style=CARD, children=[
            html.P("Tendencia mensual", style=SECTION_TITLE),
            dcc.Graph(figure=lineas, config={"displayModeBar": False}),
        ]),
        html.Div(style=CARD, children=[
            html.P("Ciudades más violentas", style=SECTION_TITLE),
            dcc.Graph(figure=barras_homicidio, config={"displayModeBar": False}),
        ]),
    ]),

    # ── Fila 3: Pie chart | Tabla top 10 causas ──────────────────────────────
    html.Div(style=ROW, children=[
        html.Div(style=CARD, children=[
            html.P("Menor índice de mortalidad", style=SECTION_TITLE),
            dcc.Graph(figure=pie_menor, config={"displayModeBar": False}),
        ]),
        html.Div(style=CARD, children=[
            html.P("Top 10 causas de muerte", style=SECTION_TITLE),
            dash_table.DataTable(
                columns=tabla["columns"],
                data=tabla["data"],
                style_header=TABLE_HEADER,
                style_cell=TABLE_CELL,
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#F9F9F9",
                    }
                ],
                style_table={"overflowX": "auto", "borderRadius": "6px", "overflow": "hidden"},
                page_size=10,
            ),
        ]),
    ]),

    # ── Fila 4: Barras apiladas (ancho completo) ─────────────────────────────
    html.Div(style=FULL, children=[
        html.Div(style=CARD, children=[
            html.P("Muertes por sexo y departamento", style=SECTION_TITLE),
            dcc.Graph(figure=barras_sexo, config={"displayModeBar": False}),
        ]),
    ]),

    # ── Fila 5: Histograma ciclo de vida (ancho completo) ────────────────────
    html.Div(style=FULL, children=[
        html.Div(style=CARD, children=[
            html.P("Distribución por ciclo de vida", style=SECTION_TITLE),
            dcc.Graph(figure=histograma, config={"displayModeBar": False}),
        ]),
    ]),

    # ── Pie de página ────────────────────────────────────────────────────────
    html.Div(
        "Datos: DANE · Estadísticas Vitales 2019 · Aplicación desarrollada con Python, Dash y Plotly",
        style={
            "textAlign": "center",
            "fontSize": "11px",
            "color": "#999",
            "padding": "20px 0 0",
        }
    ),
])


# ── Punto de entrada local ─────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)