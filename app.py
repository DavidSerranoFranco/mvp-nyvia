# MVP Nyvia 2026 - Motor de Pronostico de Demanda
# Dataset: Customer Shopping Dataset (Kaggle)
# Desarrollado por: David Serrano Franco

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

# Configuracion de la página
st.set_page_config(
    page_title="Nyvia - Pronóstico de Demanda",
    layout="wide"
)

# Titulo y descipcion
st.title("Nyvia - Motor de Pronóstico de Demanda")
st.markdown("Optimizacion de Inventario para Productos Curva A")
st.markdown("---")

# Carga de los datos (Dataset o un demo)
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
    # Puse datos simulados como un fallback, para evitar errores
    @st.cache_data
    def generar_datos_simulados():
        np.random.seed(42)
        n_registros = 5000
        fechas = pd.date_range(start="2024-01-01", end="2025-12-31", freq="D")
        
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

# Nota importante
st.info("""
    **Nota:** 
    Este prototipo utiliza datos de demostración para mostrar la capacidad de ejecucion. 
    En producción se conectaría con datos reales del ERP del Retail (ventas históricas 2 años, 
    inventario actual, etc). Mi intencion aqui es demostrar la **capacidad de ejecucion** de la propuesta.
    """)

# Procesamiento de los datos
# Guarda el total original antes de procesar
filas_originales = len(df_raw)

# Convierte fecha a datetime especificando formato DD/MM/YYYY porque antes de entregar este reto o proyecto, por el tipo de fecha que se encuentra en un mal formato o layout, pandas descarta el 69% de todos loa registros del dataset que descargue.
df_raw["invoice_date"] = pd.to_datetime(
    df_raw["invoice_date"], 
    # aqui estaba el error que comentaba anteriormente, esto es importante para formato europeo/turco
    dayfirst=True,
    errors="coerce"
)

# Verifica cauntas filas se perdieron
filas_perdidas = filas_originales - len(df_raw[df_raw["invoice_date"].notna()])

# aqui muestro una advertencia para ver si se perdieron muchas filas
# si pierde mas del 10%
if filas_perdidas > filas_originales * 0.1:
    st.warning(f"Se perdieron {filas_perdidas:,} filas por fechas inválidas ({filas_perdidas/filas_originales*100:.1f}%)")

# elimina solo las filas con fechas inválidas
df_raw = df_raw.dropna(subset=["invoice_date"])

# calcular ventas totales por transacción
df_raw["ventas_totales"] = df_raw["quantity"] * df_raw["price"]

# SIDEBAR - Filtros
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

# Filtrar los datos
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

# Proyecciones de impacto
# 10% mejora en rotación
ahorro_potencial = ventas_totales * 0.10
# 2% ventas por quiebres recuperadas
ventas_recuperadas = ventas_totales * 0.02 

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas totales", f"${ventas_totales:,.2f}")
col2.metric("Transacciones", f"{transacciones:,}")
col3.metric("Ahorro potencial (10%)", f"${ahorro_potencial:,.2f}", delta="💰")
col4.metric("Ventas a recuperar (2%)", f"${ventas_recuperadas:,.2f}", delta="📈")

st.markdown("---")



#  Gráfico de pronóstico
st.subheader("Pronóstico de Demanda - Próximas 4 Semanas")

# Agrupar ventas por mes
df["mes"] = df["invoice_date"].dt.to_period("M").astype(str)
ventas_mensuales = df.groupby("mes")["ventas_totales"].sum().reset_index()

# Pronóstico simple - promedio móvil 3 meses
ventas_mensuales["pronostico"] = ventas_mensuales["ventas_totales"].rolling(window=3).mean()
ventas_mensuales["pronostico"] = ventas_mensuales["pronostico"].fillna(ventas_mensuales["ventas_totales"].mean())

# Crear gráfico
fig = px.line(
    ventas_mensuales,
    x="mes",
    y=["ventas_totales", "pronostico"],
    labels={"mes": "Mes", "value": "Ventas (MXN)"},
    title="Ventas Históricas vs Pronóstico",
    color_discrete_map={"ventas_totales": "#0066CC", "pronostico": "#00CC66"}
)
fig.update_layout(height=400, showlegend=True, xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)




# Alertas de reposicion por categoria
st.subheader("Alertas de Reposición por Categoría")

# Agrupar por categoria
df_categoria = df.groupby("category").agg({
    "ventas_totales": "sum",
    "quantity": "sum",
    "invoice_no": "count"
}).reset_index()

df_categoria.columns = ["Categoría", "Ventas_Totales", "Cantidad_Vendida", "Transacciones"]

# Calcular prioridad - simulacion
df_categoria["Prioridad"] = df_categoria["Ventas_Totales"].apply(
    lambda x: "🟥 ALTA" if x > df_categoria["Ventas_Totales"].median() * 1.5 else ("🟨 MEDIA" if x > df_categoria["Ventas_Totales"].median() else "🟩 BAJA")
)

# Ordenar por ventas
df_categoria = df_categoria.sort_values("Ventas_Totales", ascending=False)

st.dataframe(
    df_categoria,
    use_container_width=True,
    hide_index=True
)



# Impacto economico
st.markdown("---")
st.subheader("Impacto Económico Estimado (Año 1)")

col_a, col_b, col_c = st.columns(3)
col_a.metric("Capital Liberado", "$12.5M MXN", "10% mejora rotación")
col_b.metric("Ventas Recuperadas", "$10M MXN", "2% quiebres evitados")
col_c.metric("ROI Proyectado", "6.5x", "$6.5 por cada $1 invertido")




# Footer - Informacion de contacto
st.markdown("---")
st.markdown("""
    **Prototipo MVP - Reto Analista de Datos Nyvia 2026**
    
    Presentado y desarrollado por: **David Serrano Franco**
    
    Email: david09115678@gmail.com | GitHub: https://github.com/DavidSerranoFranco/mvp-nyvia
    
    *En producción se conectaría a los datos reales del ERP del Retail.*
    """)
