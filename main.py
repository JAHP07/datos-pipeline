import time
import sys

def ejecutar_pipeline():
    inicio = time.time()

    print("\n" + "="*55)
    print("PIPELINE DE DATOS — INICIO")
    print("="*55)

    # ── FASE 1: Generar datos ────────────────────────────────
    print("\n FASE 0 — Generando dataset...")
    import src.generar_datos

    # ── FASE 1: SQL ──────────────────────────────────────────
    print("\n FASE 1 — Extracción con SQL...")
    from src.base_de_datos import conectar, crear_tablas, cargar_csv, extraer_con_sql
    conexion = conectar()
    crear_tablas(conexion)
    cargar_csv(conexion)
    extraer_con_sql(conexion)
    conexion.close()

    # ── FASE 2: Limpieza y transformación ────────────────────
    print("\n FASE 2 — Limpieza y transformación...")
    from src.limpieza import limpiar_datos, enriquecer_datos, guardar_en_sqlite
    df = limpiar_datos()
    df = enriquecer_datos(df)
    guardar_en_sqlite(df)

    # ── FASE 3: EDA ──────────────────────────────────────────
    print("\n FASE 3 — Análisis exploratorio (EDA)...")
    from src.analisis import (
        cargar_datos, estadisticas_descriptivas,
        grafico_distribuciones, grafico_ingreso_categoria,
        grafico_serie_temporal, grafico_correlaciones,
        grafico_boxplot, grafico_dispersion, grafico_region_categoria
    )
    df_limpio = cargar_datos()
    estadisticas_descriptivas(df_limpio)
    grafico_distribuciones(df_limpio)
    grafico_ingreso_categoria(df_limpio)
    grafico_serie_temporal(df_limpio)
    grafico_correlaciones(df_limpio)
    grafico_boxplot(df_limpio)
    grafico_dispersion(df_limpio)
    grafico_region_categoria(df_limpio)

    # ── FASE 5: Exportación ──────────────────────────────────
    print("\n FASE 5 — Exportación...")
    from src.exportar import exportar_csv, exportar_excel, exportar_metricas_json
    exportar_csv(df_limpio)
    exportar_excel(df_limpio)
    exportar_metricas_json(df_limpio)

    tiempo = time.time() - inicio
    print("\n" + "="*55)
    print(f"   PIPELINE COMPLETO en {tiempo:.2f} segundos")
    print("="*55)
    print("\n Outputs generados:")
    print("   reports/ventas_gold.csv")
    print("   reports/reporte_ejecutivo.xlsx")
    print("   reports/metricas.json")
    print("   reports/plots/  ← 7 gráficos PNG")

if __name__ == "__main__":
    ejecutar_pipeline()