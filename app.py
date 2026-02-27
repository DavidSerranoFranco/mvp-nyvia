# MVP Nyvia 2026 - Motor de Pronostico de Demanda
# Dataset: Customer Shopping Dataset (Kaggle)
# Desarrollado por: David Serrano Franco

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# configuracion de la pagina
st.set_page_config(
    page_title="Nyvia - Pronóstico de Demanda",
    layout="wide"
)

# titulo y descipcion
st.title("Nyvia - Motor de Pronóstico de Demanda")
st.markdown("Optimizacion de Inventario para Productos Curva A")
st.markdown("---")

# carga de los datos (Dataset o un demo)
st.sidebar.header("Fuente de datos")

opcion = st.sidebar.radio(
    "Selecciona una opcion:",
    ["Usar datos de demostracion", "Subir CSV Kaggle"]
)

if opcion == "Subir CSV Kaggle":
    uploaded_file = st.sidebar.file_uploader("Sube el archivo CSV", type=["csv"])
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.sidebar.success(f"{len(df_raw)} registros cargados")
    else:
        st.sidebar.warning("Sube algun archivo CSV para continuar")
        st.stop()
else:
    # puse datos simulados como un fallback, para evitar errores
    @st.cache_data
    def generar_datos_simulados():
        np.random.seed(42)
        n_registros = 5000
        fechas = pd.date_range(start="2025-01-01", end="2025-12-31", freq="D")
        
        datos = {
            "invoice_no": [f"I{str(i).zfill(6)}" for i in range(1, n_registros+1)],
            "customer_id": [f"C{str(np.random.randint(100000, 999999)).zfill(6)}" for _ in range(n_registros)],
            "gender": np.random.choice(["Femenino", "Masculino"], n_registros),
            "age": np.random.randint(18, 65, n_registros),
            "category": np.random.choice(["Ropa", "Zapatos", "Electronicos", "Hogar"], n_registros),
            "quantity": np.random.randint(1, 10, n_registros),
            "price": np.random.randint(500, 5000, n_registros),
            "payment_method": np.random.choice(["Tarjeta de Credito", "Tarjeta de Debito", "Efectivo"], n_registros),
            "invoice_date": np.random.choice(fechas, n_registros),
            "shopping_mall": np.random.choice(["Norte", "Sur", "Este", "Oeste"], n_registros)
        }
        return pd.DataFrame(datos)
    
    df_raw = generar_datos_simulados()
    st.sidebar.info("Uso de datos simulados para test")

# nota importante
st.info("""
    **Nota:** 
    Este prototipo utiliza datos de demostración para mostrar la capacidad de ejecucion. 
    En producción se conectaría con datos reales del ERP del Retail (ventas históricas 2 años, 
    inventario actual, etc). Mi intencion aqui es demostrar la **capacidad de ejecucion** de la propuesta.
    """)

# procesamiento de los datos
# guarda el total original antes de procesar
filas_originales = len(df_raw)

# convierte fecha a datetime especificando formato DD/MM/YYYY porque antes de entregar este reto o proyecto, por el tipo de fecha que se encuentra en un mal formato o layout, pandas descarta el 69% de todos loa registros del dataset que descargue.
df_raw["invoice_date"] = pd.to_datetime(
    df_raw["invoice_date"], 
    # aqui estaba el error que comentaba anteriormente, esto es importante para formato europeo/turco
    dayfirst=True,
    errors="coerce"
)

# verifica cauntas filas se perdieron
filas_perdidas = filas_originales - len(df_raw[df_raw["invoice_date"].notna()])

# aqui muestro una advertencia para ver si se perdieron muchas filas
# si pierde mas del 10%
if filas_perdidas > filas_originales * 0.1:
    st.warning(f"Se perdieron {filas_perdidas:,} filas por fechas inválidas ({filas_perdidas/filas_originales*100:.1f}%)")

# elimina solo las filas con fechas inválidas
df_raw = df_raw.dropna(subset=["invoice_date"])

# calcular ventas totales por transacción
df_raw["ventas_totales"] = df_raw["quantity"] * df_raw["price"]

# SIDEBAR - filtros
st.sidebar.markdown("---")
st.sidebar.header("Filtros")

categoria_seleccionada = st.sidebar.selectbox(
    "Categoria de producto",
    options=["Todas"] + sorted(df_raw["category"].unique().tolist())
)

mall_seleccionado = st.sidebar.selectbox(
    "Centro comercial",
    options=["Todos"] + sorted(df_raw["shopping_mall"].unique().tolist())
)

# filtrar los datos
df = df_raw.copy()
if categoria_seleccionada != "Todas":
    df = df[df["category"] == categoria_seleccionada]
if mall_seleccionado != "Todos":
    df = df[df["shopping_mall"] == mall_seleccionado]



#  KPIs principales
st.subheader("Indicadores clave de desempeño")

ventas_totales = df["ventas_totales"].sum()
transacciones = len(df)
ticket_promedio = df["ventas_totales"].mean()
cantidad_total = df["quantity"].sum()

# proyecciones de impacto
# 10% mejora en rotacion
ahorro_potencial = ventas_totales * 0.10
# 2% ventas por quiebres recuperadas
ventas_recuperadas = ventas_totales * 0.02 

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas totales", f"${ventas_totales:,.2f}")
col2.metric("Transacciones", f"{transacciones:,}")
col3.metric("Ahorro potencial (10%)", f"${ahorro_potencial:,.2f}", delta="💰")
col4.metric("Ventas a recuperar (2%)", f"${ventas_recuperadas:,.2f}", delta="📈")

st.markdown("---")

# grafico de proyeccion 2026
st.subheader("📈 Proyección de Ventas 2026")

st.info("""
    **📌 Metodología:**
    Proyección basada en histórico de ventas + impacto esperado de la iniciativa ($22.5M MXN).
    """)

# agrupar ventas por mes
df["mes_num"] = df["invoice_date"].dt.month

# mapeo de meses
meses_espanol = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
df["mes_nombre"] = df["mes_num"].map(meses_espanol)

# agregar ventas por mes
ventas_mensuales = df.groupby("mes_num").agg({
    "ventas_totales": "sum",
    "mes_nombre": "first"
}).reset_index()

# ordenar por número de mes
ventas_mensuales = ventas_mensuales.sort_values("mes_num")

# asignar nombre de mes
ventas_mensuales["mes"] = ventas_mensuales["mes_num"].map(meses_espanol)

# calcular promedio mensual historico
promedio_mensual = ventas_mensuales["ventas_totales"].mean()

# impacto mensual $22.5M anuales / 12 meses
impacto_mensual = 22500000 / 12

# crear proyeccion 2026
ventas_mensuales["proyeccion"] = ventas_mensuales["ventas_totales"] + impacto_mensual

# renombrar columnas para la leyenda
ventas_mensuales = ventas_mensuales.rename(columns={
    "ventas_totales": "Ventas 2025",
    "proyeccion": "Proyección 2026"
})

# crear grafico
fig = px.line(
    ventas_mensuales,
    x="mes",
    y=["Ventas 2025", "Proyección 2026"],
    labels={
        "mes": "Mes",
        "value": "Ventas (MXN)"
    },
    title="Ventas Históricas vs Proyección 2026 (+$22.5M MXN)",
    color_discrete_map={
        "Ventas 2025": "#0066CC",
        "Proyección 2026": "#00CC66"
    }
)

fig.update_layout(
    height=400,
    showlegend=True,
    xaxis_tickangle=-45,
    hovermode="x unified",
    legend=dict(x=0, y=1)
)

st.plotly_chart(fig, use_container_width=True)

# KPIs de la proyeccion
st.markdown("---")
col_p1, col_p2, col_p3 = st.columns(3)
col_p1.metric("Promedio Mensual Histórico", f"${promedio_mensual:,.0f}")
col_p2.metric("Proyección Mensual 2026", f"${promedio_mensual + impacto_mensual:,.0f}", delta=f"+${impacto_mensual:,.0f}")
col_p3.metric("Impacto Anual Esperado", "$22.5M MXN", "10% + 2% recuperación")




# alertas de reposicion curva A
st.subheader("Alertas de Reposición - Productos Curva A (Pareto 80/20)")

st.info("""
    **Ley de Pareto Aplicada:**
    El 20% de los productos (SKUs) generan aproximadamente el 80% de las ventas.
    Estos productos prioritarios se clasifican como **Curva A** y reciben atención preferencial.
    """)

# calcular ventas por SKU
df_sku = df.groupby("category").agg({
    "ventas_totales": "sum",
    "quantity": "sum",
    "invoice_no": "count"
}).reset_index()

df_sku.columns = ["Categoría", "Ventas_Totales", "Cantidad_Vendida", "Transacciones"]

# calcular % acumulado para identificar curva A (80/20)
df_sku["% Ventas"] = df_sku["Ventas_Totales"] / df_sku["Ventas_Totales"].sum() * 100
df_sku["% Acumulado"] = df_sku["% Ventas"].cumsum()

# clasificar por curva ABC
def clasificar_curva(acumulado):
    if acumulado <= 80:
        return "🟥 CURVA A (Prioritario)"
    elif acumulado <= 95:
        return "🟨 CURVA B (Medio)"
    else:
        return "🟩 CURVA C (Bajo)"

df_sku["Clasificación"] = df_sku["% Acumulado"].apply(clasificar_curva)

# ordenar por ventas descendente
df_sku = df_sku.sort_values("Ventas_Totales", ascending=False)

# mostrar solo curva A primero, eso es lo importante de todo esto
st.markdown("### 🟥 Productos Prioritarios (Curva A - 80% de ventas)")
curva_a = df_sku[df_sku["Clasificación"].str.contains("CURVA A")]
if len(curva_a) > 0:
    st.dataframe(
        curva_a[["Categoría", "Ventas_Totales", "% Ventas", "% Acumulado", "Clasificación"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("No hay suficientes datos para identificar Curva A")

# aqui muestra el resto colapsable
with st.expander("Ver Categorías Curva B y C (20% de ventas restantes)"):
    curva_bc = df_sku[df_sku["Clasificación"].str.contains("CURVA B|CURVA C")]
    st.dataframe(
        curva_bc[["Categoría", "Ventas_Totales", "% Ventas", "% Acumulado", "Clasificación"]],
        use_container_width=True,
        hide_index=True
    )

# KPI de pareto
st.markdown("---")
col_p1, col_p2 = st.columns(2)
col_p1.metric("Categorías Curva A", f"{len(curva_a)}", "80% de las ventas")
col_p2.metric("Categorías Curva B+C", f"{len(df_sku) - len(curva_a)}", "20% de las ventas")


# impacto economico
st.markdown("---")
st.subheader("Impacto Económico Estimado (Año 1)")

col_a, col_b, col_c = st.columns(3)
col_a.metric("Capital Liberado", "$12.5M MXN", "10% mejora rotación")
col_b.metric("Ventas Recuperadas", "$10M MXN", "2% quiebres evitados")
col_c.metric("ROI Proyectado", "6.5x", "$6.5 por cada $1 invertido")




# footer - informacion de contacto
st.markdown("---")
st.markdown("""
    **Prototipo MVP - Reto Analista de Datos Nyvia 2026**
    
    Presentado y desarrollado por: **David Serrano Franco**
    
    Email: david09115678@gmail.com | GitHub: https://github.com/DavidSerranoFranco/mvp-nyvia
    
    *En producción se conectaría a los datos reales del ERP del Retail.*
    """)
