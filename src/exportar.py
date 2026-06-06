import pandas as pd
import sqlite3
import json
import os

os.makedirs('reports', exist_ok=True)

def cargar_datos():
    conexion = sqlite3.connect('data/processed/pipeline.db')
    df = pd.read_sql_query("SELECT * FROM ventas_limpias", conexion)
    conexion.close()
    print(f"Datos cargados: {len(df)} registros")
    return df

def exportar_csv(df):
    ruta = 'reports/ventas_gold.csv'
    df.to_csv(ruta, index=False, encoding='utf-8-sig')
    tamanio = os.path.getsize(ruta) / 1024
    print(f"CSV exportado: ventas_gold.csv ({tamanio:.1f} KB)")

def exportar_excel(df):
    resumen_categoria = (
        df.groupby('categoria')
          .agg(
              pedidos        = ('id_pedido',  'count'),
              ingreso_total  = ('ingreso',    'sum'),
              ganancia_total = ('ganancia',   'sum'),
              margen_pct     = ('margen',     'mean'),
              descuento_pct  = ('descuento',  'mean'),
              unidades       = ('cantidad',   'sum'),
          )
          .reset_index()
    )
    resumen_categoria['margen_pct']    = (resumen_categoria['margen_pct']    * 100).round(2)
    resumen_categoria['descuento_pct'] = (resumen_categoria['descuento_pct'] * 100).round(2)

    serie_mensual = (
        df.groupby(['anio', 'mes', 'trimestre'])
          .agg(
              pedidos  = ('id_pedido', 'count'),
              ingreso  = ('ingreso',   'sum'),
              ganancia = ('ganancia',  'sum'),
              margen   = ('margen',    'mean'),
          )
          .reset_index()
    )
    serie_mensual['margen'] = (serie_mensual['margen'] * 100).round(2)

    resumen_region = (
        df.groupby(['region', 'segmento'])
          .agg(
              pedidos  = ('id_pedido', 'count'),
              ingreso  = ('ingreso',   'sum'),
              ganancia = ('ganancia',  'sum'),
          )
          .reset_index()
    )

    ruta = 'reports/reporte_ejecutivo.xlsx'
    with pd.ExcelWriter(ruta, engine='xlsxwriter') as escritor:
        libro = escritor.book

        # Formatos
        fmt_encabezado = libro.add_format({
            'bold': True, 'bg_color': '#1A56DB',
            'font_color': '#FFFFFF', 'border': 1, 'align': 'center'
        })
        fmt_moneda = libro.add_format({'num_format': '$#,##0.00', 'border': 1})
        fmt_pct    = libro.add_format({'num_format': '0.00%',     'border': 1})
        fmt_num    = libro.add_format({'num_format': '#,##0',     'border': 1})

        def escribir_hoja(df_hoja, nombre_hoja):
            df_hoja.to_excel(escritor, sheet_name=nombre_hoja, index=False, startrow=1)
            hoja = escritor.sheets[nombre_hoja]
            for num_col, nombre_col in enumerate(df_hoja.columns):
                hoja.write(0, num_col, nombre_col, fmt_encabezado)
                hoja.set_column(num_col, num_col, max(14, len(nombre_col) + 2))

        escribir_hoja(df,                 'Datos Gold')
        escribir_hoja(resumen_categoria,  'Resumen Categoría')
        escribir_hoja(serie_mensual,      'Serie Mensual')
        escribir_hoja(resumen_region,     'Región y Segmento')

    tamanio = os.path.getsize(ruta) / 1024
    print(f" Excel exportado: reporte_ejecutivo.xlsx ({tamanio:.1f} KB) — 4 hojas")

def exportar_metricas_json(df):
    metricas = {
        "dataset": {
            "total_registros":  int(len(df)),
            "fecha_desde":      str(df['fecha'].min()),
            "fecha_hasta":      str(df['fecha'].max()),
        },
        "ingresos": {
            "total_clp":        round(float(df['ingreso'].sum()), 2),
            "promedio_pedido":  round(float(df['ingreso'].mean()), 2),
            "maximo_pedido":    round(float(df['ingreso'].max()), 2),
        },
        "rentabilidad": {
            "ganancia_total_clp":   round(float(df['ganancia'].sum()), 2),
            "margen_promedio_pct":  round(float(df['margen'].mean() * 100), 2),
            "mejor_categoria":      str(df.groupby('categoria')['margen'].mean().idxmax()),
            "region_top_ingreso":   str(df.groupby('region')['ingreso'].sum().idxmax()),
        },
        "calidad": {
            "valores_atipicos":  int(df['es_atipico'].sum()),
            "pedidos_premium":   int((df['nivel_pedido'] == 'Premium').sum()),
        }
    }

    ruta = 'reports/metricas.json'
    with open(ruta, 'w', encoding='utf-8') as archivo:
        json.dump(metricas, archivo, indent=2, ensure_ascii=False)

    print(f"\nKPIs exportados a metricas.json:")
    print(f"   Total registros:    {metricas['dataset']['total_registros']:,}")
    print(f"   Ingreso total:      ${metricas['ingresos']['total_clp']:,.2f}")
    print(f"   Margen promedio:    {metricas['rentabilidad']['margen_promedio_pct']}%")
    print(f"   Mejor categoría:    {metricas['rentabilidad']['mejor_categoria']}")
    print(f"   Región top:         {metricas['rentabilidad']['region_top_ingreso']}")
    print(f"   Valores atípicos:   {metricas['calidad']['valores_atipicos']}")

if __name__ == "__main__":
    print("="*50)
    print("FASE 5 — EXPORTACIÓN")
    print("="*50)
    df = cargar_datos()
    exportar_csv(df)
    exportar_excel(df)
    exportar_metricas_json(df)
    print("\nExportación completa")