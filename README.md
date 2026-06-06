# 📊 Pipeline de Datos de Ventas

[![Python 3.14](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-3.0.1-red)](https://pandas.pydata.org/)
[![SQLite 3.50+](https://img.shields.io/badge/SQLite-3-green)](https://www.sqlite.org/)
[![Matplotlib 3.10](https://img.shields.io/badge/Matplotlib-3.5-orange)](https://matplotlib.org/)

Pipeline ETL completo que **simula un proceso real de análisis de datos de ventas**. Extrae datos generados aleatoriamente, los transforma aplicando limpieza, agregaciones con SQL y Python, y genera informes visuales y tabulares.

> ✅ habilidades en **Python, Pandas, SQL, automatización y visualización de datos**.

---

## 🚀 ¿Qué hace este pipeline?

1. **Genera** un dataset simulado de ventas (productos, categorías, precios, cantidades).
2. **Limpia y transforma** los datos:
   - Elimina registros duplicados.
   - Filtra valores atípicos.
   - Calcula columnas derivadas (ingresos totales, mes de venta, etc.).
3. **Carga** los datos limpios a una base SQLite.
4. **Ejecuta consultas SQL** para obtener:
   - Ventas por categoría.
   - Top 5 productos más vendidos.
   - Evolución mensual de ingresos.
5. **Genera reportes**:
   - Tablas en CSV.
   - Gráficos de barras y líneas guardados en `/reportes/plots`.

---

## 🛠️ Tecnologías utilizadas

| Herramienta     | Propósito                          |
|----------------|------------------------------------|
| Python          | Lenguaje principal                 |
| Pandas          | Manipulación y análisis de datos   |
| SQLite3         | Base de datos relacional ligera    |
| Matplotlib      | Visualización de resultados        |
| Random / Faker  | Generación de datos simulados      |


---

## ⚙️ Cómo ejecutarlo.

```bash
# 1. Clonar el repositorio
git clone https://github.com/JAHP07/datos-pipeline.git
cd datos-pipeline

# 2. Crear un entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el pipeline completo
python main.py


Después de la ejecución:

1. **Los datos limpios estarán en data/ventas_limpias.csv**

2. **Los reportes tabulares en /reportes/*.csv**

3. **Los gráficos en /reportes/plots/**


---

🗂️ Estructura del Repositorio.

datos-pipeline/
│
├── main.py                        ← Ejecuta el pipeline completo
├── requirements.txt               ← Dependencias
├── .gitignore
│
├── src/
│   ├── generar_datos.py           ← Genera dataset sintético
│   ├── base_de_datos.py           ← Fase 1: SQL + SQLite
│   ├── limpieza.py                ← Fases 2–3: Pandas + features
│   ├── analisis.py                ← Fase 4: EDA + 7 gráficos
│   └── exportar.py                ← Fase 6: CSV, Excel, JSON
│
├── data/
│   ├── raw/                       ← CSV de entrada
│   └── processed/pipeline.db     ← Base de datos SQLite
│
└── reportes/
    ├── ventas_gold.csv            ← Dataset listo para Power BI
    ├── reporte_ejecutivo.xlsx     ← Excel multi-hoja
    ├── metricas.json              ← KPIs del último run
    └── plots/                     ← 7 gráficos PNG del EDA
