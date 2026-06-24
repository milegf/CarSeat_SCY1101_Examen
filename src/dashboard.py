"""Dashboard interactivo de ventas para el dataset Car Seats (Plotly Dash).

Uso:
    python src/dashboard.py            -> corre solo local (http://127.0.0.1:8050)
    python src/dashboard.py --ngrok    -> además intenta levantar un túnel público con ngrok
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "carseats_clp.csv"

COLUMNAS_CATEGORICAS = ["ShelveLoc", "Urban", "US"]

# ---------------------------------------------------------------------------
# Tema visual: claro y suave
# ---------------------------------------------------------------------------
COLOR_FONDO = "#F4F6F8"
COLOR_TARJETA = "#FFFFFF"
COLOR_TEXTO_SECUNDARIO = "#5A6472"
PALETA_COLORES = ["#5DADE2", "#48C9B0", "#F5B197", "#A78BFA"]

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = PALETA_COLORES

# Reglas de tamaño de los gráficos
ALTURA_GRAFICO = 380
CONFIG_GRAFICO = {}

ESTILO_FILA_GRAFICOS = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
    "gap": "16px",
}


def cargar_datos(ruta):
    try:
        return pd.read_csv(ruta)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"No se encontró el dataset procesado en {ruta}. "
            "Corre primero el notebook (Sección 1, ETL) para generarlo."
        )


def clasificar_ventaja_precio(diferencial):
    if diferencial > 5000:
        return "Más barato que competencia"
    elif diferencial < -5000:
        return "Más caro que competencia"
    return "Precio similar"


def clasificar_nivel_publicidad(advertising):
    if advertising == 0:
        return "Sin publicidad"
    elif advertising <= 10000:
        return "Publicidad moderada"
    return "Publicidad alta"


df = cargar_datos(DATA_PATH)
df["ventaja_precio"] = (df["CompPrice"] - df["Price"]).apply(clasificar_ventaja_precio)
df["nivel_publicidad"] = df["Advertising"].apply(clasificar_nivel_publicidad)

ORDEN_VENTAJA_PRECIO = ["Más caro que competencia", "Precio similar", "Más barato que competencia"]
ORDEN_NIVEL_PUBLICIDAD = ["Sin publicidad", "Publicidad moderada", "Publicidad alta"]

app = Dash(__name__)
app.title = "Dashboard Car Seats"

ESTILO_PAGINA = {
    "backgroundColor": COLOR_FONDO,
    "minHeight": "100vh",
    "fontFamily": "Segoe UI, sans-serif",
    "padding": "0 0 30px 0",
}


def grafico(figura=None, id_grafico=None):
    """Crea un dcc.Graph siguiendo siempre la misma regla de tamaño."""
    kwargs = {"id": id_grafico} if id_grafico else {}
    if figura is not None:
        kwargs["figure"] = figura
    return dcc.Graph(config=CONFIG_GRAFICO, style={"width": "100%", "height": f"{ALTURA_GRAFICO}px"}, **kwargs)


def grafico_con_insight(figura, texto_insight):
    """Gráfico + una frase corta debajo con la conclusión"""
    return html.Div(
        [
            grafico(figura=figura),
            html.P(
                texto_insight,
                style={
                    "fontSize": "13px",
                    "fontStyle": "italic",
                    "color": COLOR_TEXTO_SECUNDARIO,
                    "margin": "4px 8px 0 8px",
                },
            ),
        ],
        style={"minWidth": "0"},
    )


# ---------------------------------------------------------------------------
# Vista Ejecutiva: KPIs + 3 conclusiones de negocio, sin filtros
# ---------------------------------------------------------------------------


def tarjeta_kpi(titulo, valor):
    return html.Div(
        [
            html.P(titulo, style={"margin": "0", "fontSize": "14px", "color": COLOR_TEXTO_SECUNDARIO}),
            html.H2(valor, style={"margin": "0", "color": "#2C3E50"}),
        ],
        style={
            "backgroundColor": COLOR_TARJETA,
            "borderRadius": "12px",
            "padding": "18px",
            "textAlign": "center",
            "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
        },
    )


def construir_vista_ejecutiva():
    ventas_shelveloc = df.groupby("ShelveLoc")["Sales"].mean().reindex(["Bad", "Medium", "Good"])

    fig_shelveloc = px.bar(
        ventas_shelveloc.reset_index(),
        x="ShelveLoc",
        y="Sales",
        category_orders={"ShelveLoc": ["Bad", "Medium", "Good"]},
        labels={"ShelveLoc": "Ubicación en Estantería", "Sales": "Ventas Promedio (miles u.)"},
        title="Ventas por Ubicación en Estantería",
        color="ShelveLoc",
        height=ALTURA_GRAFICO,
    )
    fig_shelveloc.update_layout(showlegend=False)

    ventaja_highsales = df.groupby("ventaja_precio")["HighSales"].mean().reindex(ORDEN_VENTAJA_PRECIO) * 100
    fig_ventaja_precio = px.bar(
        ventaja_highsales.reset_index(),
        x="ventaja_precio",
        y="HighSales",
        labels={"ventaja_precio": "Posición de Precio vs Competencia", "HighSales": "% Ventas Altas"},
        title="¿Conviene ser más barato que la competencia?",
        color="ventaja_precio",
        height=ALTURA_GRAFICO,
    )
    fig_ventaja_precio.update_layout(showlegend=False)

    publicidad_highsales = df.groupby("nivel_publicidad")["HighSales"].mean().reindex(ORDEN_NIVEL_PUBLICIDAD) * 100
    fig_publicidad = px.bar(
        publicidad_highsales.reset_index(),
        x="nivel_publicidad",
        y="HighSales",
        labels={"nivel_publicidad": "Inversión en Publicidad", "HighSales": "% Ventas Altas"},
        title="Publicidad: ¿vale la pena invertir más?",
        color="nivel_publicidad",
        height=ALTURA_GRAFICO,
    )
    fig_publicidad.update_layout(showlegend=False)

    ingreso_total_millones = (df["Price"] * df["Sales"]).sum() / 1000

    kpis = html.Div(
        [
            tarjeta_kpi("N° de Tiendas", f"{len(df)}"),
            tarjeta_kpi("Ventas Promedio", f"{df['Sales'].mean():.1f} mil u."),
            tarjeta_kpi("Ingreso Total Estimado", f"${ingreso_total_millones:,.0f} M CLP"),
            tarjeta_kpi("Tiendas con Ventas Altas", f"{df['HighSales'].mean() * 100:.1f}%"),
        ],
        style={**ESTILO_FILA_GRAFICOS, "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "marginBottom": "24px"},
    )

    graficos = html.Div(
        [
            grafico_con_insight(
                fig_shelveloc,
                f"Las tiendas con buena ubicación venden en promedio {ventas_shelveloc['Good']:.1f} mil unidades, "
                f"casi el doble que las de ubicación mala ({ventas_shelveloc['Bad']:.1f} mil).",
            ),
            grafico_con_insight(
                fig_ventaja_precio,
                "Las tiendas más baratas que la competencia alcanzan 56% de ventas altas, "
                "frente a solo 16% en las más caras.",
            ),
            grafico_con_insight(
                fig_publicidad,
                "Invertir en publicidad alta casi duplica la probabilidad de ventas altas "
                "(61% vs 31% sin publicidad).",
            ),
        ],
        style=ESTILO_FILA_GRAFICOS,
    )

    return html.Div(
        [
            html.H3("Resumen General"),
            kpis,
            html.H3("Conclusiones Clave", style={"marginTop": "8px"}),
            graficos,
        ],
        style={"padding": "20px"},
    )


# ---------------------------------------------------------------------------
# Vista Analítica: un filtro categórico que mueve los 3 gráficos
# ---------------------------------------------------------------------------


def construir_vista_analitica():
    return html.Div(
        [
            html.H3("Explora la Relación entre Variables y las Ventas"),
            html.P(
                "Elige una variable para explorar cómo se relaciona con las ventas y el precio.",
                style={"color": COLOR_TEXTO_SECUNDARIO},
            ),
            dcc.Dropdown(
                id="filtro-categoria",
                options=[{"label": col, "value": col} for col in COLUMNAS_CATEGORICAS],
                value="ShelveLoc",
                clearable=False,
                style={"width": "300px", "marginBottom": "16px"},
            ),
            html.Div(
                [
                    grafico(id_grafico="grafico-ventas-categoria"),
                    grafico(id_grafico="grafico-highsales-categoria"),
                    grafico(id_grafico="grafico-precio-ventas"),
                ],
                style=ESTILO_FILA_GRAFICOS,
            ),
        ],
        style={"padding": "20px"},
    )


app.layout = html.Div(
    [
        html.H1("Dashboard de Ventas — Car Seats", style={"padding": "20px 20px 0 20px", "color": "#2C3E50"}),
        dcc.Tabs(
            id="tabs-principal",
            value="ejecutiva",
            children=[
                dcc.Tab(label="Vista Ejecutiva", value="ejecutiva"),
                dcc.Tab(label="Vista Analítica", value="analitica"),
            ],
        ),
        html.Div(id="contenido-tab"),
    ],
    style=ESTILO_PAGINA,
)


@app.callback(
    Output("contenido-tab", "children"),
    Input("tabs-principal", "value"),
)
def renderizar_tab(tab_activa):
    """Solo monta el contenido de la pestaña activa (ver nota junto a CONFIG_GRAFICO)."""
    if tab_activa == "analitica":
        return construir_vista_analitica()
    return construir_vista_ejecutiva()


@app.callback(
    Output("grafico-ventas-categoria", "figure"),
    Output("grafico-highsales-categoria", "figure"),
    Output("grafico-precio-ventas", "figure"),
    Input("filtro-categoria", "value"),
)
def actualizar_graficos_categoria(categoria):
    ventas_promedio = df.groupby(categoria)["Sales"].mean().reset_index()
    fig_ventas = px.bar(
        ventas_promedio,
        x=categoria,
        y="Sales",
        labels={"Sales": "Ventas Promedio (miles u.)"},
        title=f"Ventas Promedio por {categoria}",
        color=categoria,
        height=ALTURA_GRAFICO,
    )
    fig_ventas.update_layout(showlegend=False)

    proporcion = (pd.crosstab(df[categoria], df["HighSales"], normalize="index") * 100).reset_index()
    proporcion = proporcion.melt(id_vars=categoria, var_name="HighSales", value_name="Porcentaje")
    proporcion["HighSales"] = proporcion["HighSales"].map({0: "Bajas", 1: "Altas"})
    fig_highsales = px.bar(
        proporcion,
        x=categoria,
        y="Porcentaje",
        color="HighSales",
        barmode="stack",
        title=f"% Ventas Altas/Bajas por {categoria}",
        height=ALTURA_GRAFICO,
    )

    fig_precio_ventas = px.scatter(
        df,
        x="Price",
        y="Sales",
        color=categoria,
        labels={"Price": "Precio (CLP)", "Sales": "Ventas (miles u.)"},
        title=f"Precio vs Ventas, coloreado por {categoria}",
        height=ALTURA_GRAFICO,
    )

    return fig_ventas, fig_highsales, fig_precio_ventas


def iniciar_ngrok(puerto):
    try:
        from pyngrok import ngrok

        url_publica = ngrok.connect(puerto)
        print(f"Túnel ngrok activo: {url_publica}")
    except Exception as error:
        print(f"No se pudo levantar el túnel de ngrok ({error}). El dashboard sigue disponible solo en local.")


if __name__ == "__main__":
    PUERTO = 8050

    if "--ngrok" in sys.argv:
        iniciar_ngrok(PUERTO)

    # debug=False: evita que el reloader de Flask reinicie el proceso y duplique el túnel de ngrok
    app.run(debug=False, port=PUERTO)
