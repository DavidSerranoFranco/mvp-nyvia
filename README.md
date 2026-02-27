# Nyvia 2026 - Motor de Pronóstico de Demanda

**Reto Analista de Datos | Propuesta de Optimización de Inventario para Retail**

---

## Objetivo del Proyecto

Este prototipo fue desarrollado como parte del **Reto Analista de Datos 2026 de Nyvia**. 

Demuestra la viabilidad de implementar un **Motor de Pronóstico de Demanda** para optimizar inventarios en una empresa de retail mexicana con ventas anuales de ~$500M MXN.

---

**Prueba el prototipo desplegado:**

🔗 **[https://mvp-nyvia-by464jttb2roviv78dlljj.streamlit.app/](https://mvp-nyvia-by464jttb2roviv78dlljj.streamlit.app/)**

*(Haz clic para abrir la aplicación en Streamlit Cloud)*

> **Nota:** El prototipo permite cargar datos reales vía CSV. Para demostración rápida, usa la opción "Datos de demostración".

---

## Propuesta de Valor

| **Problema** | **Solución** | **Impacto Esperado** |
| :--- | :--- | :--- |
| Decisiones de compra basadas en intuición y Excel | Dashboard interactivo con pronóstico | Liberar ~$12.5M MXN en capital de trabajo |
| Quiebres de stock en productos clave | Alertas de reposición prioritaria | Recuperar ~$10M MXN en ventas perdidas |
| Sin visibilidad de demanda futura | Pronóstico basado en datos históricos | **ROI proyectado: 6.5x en Año 1** |

---

## Funcionalidades del MVP

- **Pronóstico de Demanda:** Proyección de ventas
- **Alertas de Reposición:** Identificación de productos con riesgo de quiebre de stock
- **KPIs de Impacto:** Visualización de ahorro potencial y ventas recuperadas
- **Filtros Interactivos:** Por categoría, centro comercial y período
- **Carga Flexible de Datos:** Soporta datos simulados o CSV personalizado

---

## Datos Utilizados

**Para este prototipo de demostración:**

| **Fuente** | **Propósito** | **Nota** |
| :--- | :--- | :--- |
| Datos Simulados | Demostración inmediata | Generados con distribuciones realistas |
| Dataset Público (Kaggle) | Validación con datos reales | Customer Shopping Dataset |
| **En Producción** | **ERP real de la empresa** | **Ventas históricas 2 años + Inventario actual** |

> **Transparencia:** Este MVP utiliza datos de demostración. En un escenario real, se conectaría directamente a los datos del ERP de la empresa.

---

## Tecnologías Utilizadas

| **Tecnología** | **Propósito** |
| :--- | :--- |
| Python 3.11+ | Lenguaje principal |
| Streamlit | Dashboard interactivo |
| Pandas | Manipulación de datos |
| NumPy | Cálculos numéricos |
| Plotly | Visualizaciones interactivas |

---

## Instalación y Ejecución Local

### Prerrequisitos
- Python 3.11 o superior
- pip (gestor de paquetes)

### Pasos

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/DavidSerranoFranco/mvp-nyvia.git
   cd nyvia-mvp-2026

<p align="center">
  <em>Desarrollado con 💙 para el Reto Nyvia 2026</em>
</p>