import pandas as pd
import numpy as np
import sqlite3

def limpiar_datos():
    print("="*50)
    print("FASE 2 — LIMPIEZA Y TRANSFORMACIÓN CON PANDAS")
    print("="*50)

    df = pd.read_csv('data/raw/ventas_raw.csv')
    print(f"\n Dataset original: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"\nNulos antes de limpiar:")
    print(df.isnull().sum())

    # ── PASO 1: Tipos de datos correctos ─────────────────────
    df['fecha']       = pd.to_datetime(df['fecha'])
    df['id_pedido']   = df['id_pedido'].astype(int)
    df['id_cliente']  = df['id_cliente'].astype(int)
    df['cantidad']    = df['cantidad'].astype(int)
    print("\n Paso 1 — Tipos de datos corregidos")

    # ── PASO 2: Eliminar duplicados ───────────────────────────
    filas_antes = len(df)
    df = df.drop_duplicates(subset=['id_pedido'], keep='first')
    eliminados = filas_antes - len(df)
    print(f" Paso 2 — Duplicados eliminados: {eliminados}")

    # ── PASO 3: Imputar precio_unit con mediana por categoría ─
    nulos_precio = df['precio_unit'].isna().sum()
    df['precio_unit'] = df.groupby('categoria')['precio_unit'].transform(
        lambda x: x.fillna(x.median())
    )
    print(f" Paso 3 — precio_unit imputados con mediana por categoría: {nulos_precio}")

    # ── PASO 4: Imputar descuento con mediana por segmento ────
    nulos_desc = df['descuento'].isna().sum()
    df['descuento'] = df.groupby('segmento')['descuento'].transform(
        lambda x: x.fillna(x.median())
    )
    print(f" Paso 4 — descuento imputados con mediana por segmento: {nulos_desc}")

    print(f"\nNulos después de limpiar: {df.isnull().sum().sum()}")
    print(f"Filas finales: {len(df)}")
    return df

def enriquecer_datos(df):
    print("\n" + "="*50)
    print("FASE 2b — FEATURE ENGINEERING")
    print("="*50)

    # ── Columnas de tiempo ────────────────────────────────────
    df['anio']      = df['fecha'].dt.year
    df['mes']       = df['fecha'].dt.month
    df['trimestre'] = df['fecha'].dt.quarter
    print(" Columnas de tiempo: anio, mes, trimestre")

    # ── Métricas financieras ──────────────────────────────────
    df['ingreso']  = (df['cantidad'] * df['precio_unit'] * (1 - df['descuento'])).round(2)
    df['costo']    = (df['ingreso'] * df['ratio_costo']).round(2)
    df['ganancia'] = (df['ingreso'] - df['costo']).round(2)
    df['margen']   = (df['ganancia'] / df['ingreso']).round(4)
    print(" Métricas financieras: ingreso, costo, ganancia, margen")

    # ── Lógica de negocio: impuesto diferente por región ──────
    tasa_por_region = {
        'Norte':  0.19,
        'Sur':    0.19,
        'Este':   0.21,
        'Oeste':  0.18,
        'Centro': 0.19,
    }
    df['tasa_impuesto'] = df['region'].map(tasa_por_region)
    df['ganancia_neta'] = (df['ganancia'] * (1 - df['tasa_impuesto'])).round(2)
    df['margen_neto']   = (df['ganancia_neta'] / df['ingreso']).round(4)
    print(" Lógica de negocio: tasa_impuesto por región, ganancia_neta, margen_neto")

    # ── Segmentación del pedido por valor ─────────────────────
    df['nivel_pedido'] = pd.cut(
        df['ingreso'],
        bins=[0, 50, 200, 1000, float('inf')],
        labels=['Bajo', 'Medio', 'Alto', 'Premium']
    ).astype(str)
    print(" Segmentación: nivel_pedido (Bajo / Medio / Alto / Premium)")

    # ── Detección de valores atípicos con Z-score ─────────────
    media  = df['ingreso'].mean()
    desvio = df['ingreso'].std()
    df['es_atipico'] = (abs((df['ingreso'] - media) / desvio) > 2.5).astype(int)
    print(f" Outliers detectados (z > 2.5): {df['es_atipico'].sum()}")

    print(f"\nResumen financiero:")
    print(df[['ingreso', 'ganancia', 'margen', 'ganancia_neta']].describe().round(2))
    return df

def guardar_en_sqlite(df):
    print("\n" + "="*50)
    print("FASE 4 — CARGA A SQLITE (ventas_limpias)")
    print("="*50)

    conexion = sqlite3.connect('data/processed/pipeline.db')

    df_db = df.copy()
    df_db['fecha'] = df_db['fecha'].dt.strftime('%Y-%m-%d')

    conexion.execute("DELETE FROM ventas_limpias")
    df_db.to_sql('ventas_limpias', conexion, if_exists='append', index=False)
    conexion.commit()

    total = conexion.execute("SELECT COUNT(*) FROM ventas_limpias").fetchone()[0]
    print(f" ventas_limpias cargada: {total} registros")

    # Verificar con SQL analítico
    print("\n Verificación SQL — Ranking por ingreso:")
    verificacion = pd.read_sql_query("""
        SELECT
            categoria,
            COUNT(*)                          AS pedidos,
            ROUND(SUM(ingreso), 2)            AS ingreso_total,
            ROUND(AVG(margen) * 100, 2)       AS margen_pct,
            RANK() OVER (
                ORDER BY SUM(ingreso) DESC
            )                                 AS ranking
        FROM ventas_limpias
        GROUP BY categoria
        ORDER BY ingreso_total DESC
    """, conexion)
    print(verificacion.to_string(index=False))

    # Generar y guardar resumen mensual
    resumen = pd.read_sql_query("""
        SELECT
            anio, mes, trimestre, categoria, region,
            COUNT(*)                    AS total_pedidos,
            ROUND(SUM(ingreso), 2)      AS ingreso_total,
            ROUND(SUM(costo), 2)        AS costo_total,
            ROUND(SUM(ganancia), 2)     AS ganancia_total,
            ROUND(AVG(margen), 4)       AS margen_promedio
        FROM ventas_limpias
        GROUP BY anio, mes, trimestre, categoria, region
        ORDER BY anio, mes
    """, conexion)

    conexion.execute("DELETE FROM resumen_mensual")
    resumen.to_sql('resumen_mensual', conexion, if_exists='append', index=False)
    conexion.commit()
    print(f"\n resumen_mensual cargado: {len(resumen)} filas")

    conexion.close()
    return df

if __name__ == "__main__":
    df = limpiar_datos()
    df = enriquecer_datos(df)
    guardar_en_sqlite(df)
    print("\n Fases 2, 3 y 4 completas")