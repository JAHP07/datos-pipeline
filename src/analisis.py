import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import sqlite3
import os

os.makedirs('reports/plots', exist_ok=True)

# ── Configuración visual ──────────────────────────────────────
colores = ['#1A56DB', '#F05252', '#31C48D', '#FF8A4C', '#9061F9', '#E74694', '#0E9F6E']
sns.set_theme(style='whitegrid', font_scale=1.1)
plt.rcParams.update({
    'figure.dpi':        150,
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'figure.facecolor':  'white',
})

def cargar_datos():
    conexion = sqlite3.connect('data/processed/pipeline.db')
    df = pd.read_sql_query("SELECT * FROM ventas_limpias", conexion)
    conexion.close()
    df['fecha'] = pd.to_datetime(df['fecha'])
    print(f"Datos cargados desde SQLite: {len(df)} registros")
    return df

def estadisticas_descriptivas(df):
    print("\n" + "="*50)
    print("ESTADÍSTICAS DESCRIPTIVAS")
    print("="*50)
    columnas = ['ingreso', 'ganancia', 'margen', 'cantidad', 'precio_unit', 'descuento']
    estadisticas = df[columnas].describe(percentiles=[.25, .5, .75, .95]).T
    estadisticas['asimetria']  = df[columnas].skew()
    estadisticas['curtosis']   = df[columnas].kurtosis()
    print(estadisticas.round(4).to_string())
    return estadisticas

# ── GRÁFICO 1: Distribuciones ─────────────────────────────────
def grafico_distribuciones(df):
    fig, ejes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('Distribución de Métricas Clave', fontsize=16, fontweight='bold')

    metricas = [
        ('ingreso',      'Ingreso (CLP)'),
        ('ganancia',     'Ganancia Bruta (CLP)'),
        ('margen',       'Margen de Ganancia'),
        ('descuento',    'Descuento Aplicado'),
    ]

    for eje, (columna, etiqueta), color in zip(ejes.flatten(), metricas, colores):
        datos = df[columna].dropna()
        eje.hist(datos, bins=40, color=color, alpha=0.75, edgecolor='white')
        eje.axvline(datos.mean(),   color='black', lw=2, ls='--', label=f'Media: {datos.mean():.2f}')
        eje.axvline(datos.median(), color='gray',  lw=2, ls=':',  label=f'Mediana: {datos.median():.2f}')
        eje.set_xlabel(etiqueta)
        eje.set_ylabel('Frecuencia')
        eje.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig('reports/plots/01_distribuciones.png', bbox_inches='tight')
    plt.show()
    print("💾 Guardado: 01_distribuciones.png")

# ── GRÁFICO 2: Ingreso por categoría ─────────────────────────
def grafico_ingreso_categoria(df):
    agrupado = (df.groupby('categoria')
                  .agg(ingreso=('ingreso', 'sum'), margen=('margen', 'mean'))
                  .sort_values('ingreso', ascending=True))

    fig, eje = plt.subplots(figsize=(11, 5))
    barras = eje.barh(agrupado.index, agrupado['ingreso'],
                      color=colores[:len(agrupado)], edgecolor='white')

    for barra, (_, fila) in zip(barras, agrupado.iterrows()):
        eje.text(
            barra.get_width() + agrupado['ingreso'].max() * 0.01,
            barra.get_y() + barra.get_height() / 2,
            f"${barra.get_width():,.0f}  ({fila['margen']*100:.1f}%)",
            va='center', fontsize=9
        )

    eje.set_title('Ingreso Total por Categoría (con % Margen)', fontsize=14, fontweight='bold')
    eje.set_xlabel('Ingreso (CLP)')
    eje.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    plt.savefig('reports/plots/02_ingreso_categoria.png', bbox_inches='tight')
    plt.show()
    print("Guardado: 02_ingreso_categoria.png")

# ── GRÁFICO 3: Serie temporal mensual ────────────────────────
def grafico_serie_temporal(df):
    serie = (df.groupby(['anio', 'mes'])
               .agg(ingreso=('ingreso', 'sum'), ganancia=('ganancia', 'sum'))
               .reset_index())
    serie['periodo'] = pd.to_datetime(
        serie['anio'].astype(str) + '-' + serie['mes'].astype(str).str.zfill(2)
    )
    serie = serie.sort_values('periodo')

    fig, eje1 = plt.subplots(figsize=(13, 5))
    eje1.fill_between(serie['periodo'], serie['ingreso'], alpha=0.15, color=colores[0])
    eje1.plot(serie['periodo'], serie['ingreso'], color=colores[0], lw=2.5, label='Ingreso')
    eje2 = eje1.twinx()
    eje2.plot(serie['periodo'], serie['ganancia'], color=colores[1], lw=2, ls='--', label='Ganancia')

    eje1.set_title('Evolución Mensual: Ingreso vs Ganancia Bruta', fontsize=14, fontweight='bold')
    eje1.set_ylabel('Ingreso (CLP)', color=colores[0])
    eje2.set_ylabel('Ganancia (CLP)', color=colores[1])
    eje1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    eje2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    lineas = eje1.get_lines() + eje2.get_lines()
    eje1.legend(lineas, [l.get_label() for l in lineas], loc='upper left')
    plt.tight_layout()
    plt.savefig('reports/plots/03_serie_temporal.png', bbox_inches='tight')
    plt.show()
    print("Guardado: 03_serie_temporal.png")

# ── GRÁFICO 4: Mapa de correlaciones ─────────────────────────
def grafico_correlaciones(df):
    columnas_num = ['ingreso', 'ganancia', 'margen', 'cantidad', 'precio_unit', 'descuento', 'ratio_costo']
    correlacion  = df[columnas_num].corr()
    mascara      = np.triu(np.ones_like(correlacion, dtype=bool))

    fig, eje = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        correlacion, mask=mascara, annot=True, fmt='.2f',
        cmap='RdYlGn', center=0, linewidths=0.5,
        ax=eje, annot_kws={'size': 9}
    )
    eje.set_title('Mapa de Correlaciones entre Variables Numéricas', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('reports/plots/04_correlaciones.png', bbox_inches='tight')
    plt.show()
    print("Guardado: 04_correlaciones.png")

# ── GRÁFICO 5: Boxplot outliers por categoría ────────────────
def grafico_boxplot(df):
    orden = df.groupby('categoria')['ingreso'].median().sort_values(ascending=False).index

    fig, eje = plt.subplots(figsize=(12, 5))
    sns.boxplot(
        data=df, x='categoria', y='ingreso', order=orden,
        palette=colores[:len(orden)],
        flierprops={'marker': 'o', 'markersize': 3, 'alpha': 0.5},
        ax=eje
    )
    eje.set_title('Distribución de Ingreso por Categoría (con Valores Atípicos)', fontsize=14, fontweight='bold')
    eje.set_xlabel('Categoría')
    eje.set_ylabel('Ingreso (CLP)')
    eje.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.xticks(rotation=25)
    plt.tight_layout()
    plt.savefig('reports/plots/05_boxplot.png', bbox_inches='tight')
    plt.show()
    print(" Guardado: 05_boxplot.png")

# ── GRÁFICO 6: Scatter ingreso vs margen ─────────────────────
def grafico_dispersion(df):
    muestra    = df.sample(min(1000, len(df)), random_state=42)
    categorias = df['categoria'].unique()
    mapa_color = {cat: colores[i % len(colores)] for i, cat in enumerate(categorias)}

    fig, eje = plt.subplots(figsize=(11, 6))
    for cat in categorias:
        sub = muestra[muestra['categoria'] == cat]
        eje.scatter(sub['ingreso'], sub['margen'], label=cat,
                    alpha=0.6, s=30, color=mapa_color[cat])

    eje.axhline(df['margen'].mean(), color='#555', ls='--', lw=1.5,
                label=f"Margen promedio: {df['margen'].mean()*100:.1f}%")
    eje.set_title('Ingreso vs Margen de Ganancia por Categoría', fontsize=14, fontweight='bold')
    eje.set_xlabel('Ingreso (CLP)')
    eje.set_ylabel('Margen de Ganancia')
    eje.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    eje.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))
    eje.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig('reports/plots/06_dispersion.png', bbox_inches='tight')
    plt.show()
    print(" Guardado: 06_dispersion.png")

# ── GRÁFICO 7: Heatmap región x categoría ────────────────────
def grafico_region_categoria(df):
    tabla = df.pivot_table(
        index='region', columns='categoria',
        values='ganancia', aggfunc='sum'
    ).fillna(0)

    fig, eje = plt.subplots(figsize=(13, 5))
    sns.heatmap(
        tabla / 1000, annot=True, fmt='.1f',
        cmap='YlOrRd', linewidths=0.5,
        ax=eje, annot_kws={'size': 9}
    )
    eje.set_title('Ganancia Bruta (miles CLP) — Región  Categoría', fontsize=14, fontweight='bold')
    eje.set_xlabel('Categoría')
    eje.set_ylabel('Región')
    plt.tight_layout()
    plt.savefig('reports/plots/07_region_categoria.png', bbox_inches='tight')
    plt.show()
    print(" Guardado: 07_region_categoria.png")

# ── Pipeline EDA completo ─────────────────────────────────────
if __name__ == "__main__":
    df = cargar_datos()
    estadisticas = estadisticas_descriptivas(df)

    print("\n" + "="*50)
    print("FASE 3 — EDA: GENERANDO GRÁFICOS")
    print("="*50)

    grafico_distribuciones(df)
    grafico_ingreso_categoria(df)
    grafico_serie_temporal(df)
    grafico_correlaciones(df)
    grafico_boxplot(df)
    grafico_dispersion(df)
    grafico_region_categoria(df)

    print("\n EDA completo — 7 gráficos guardados en reports/plots/")