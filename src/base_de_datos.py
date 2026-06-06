import sqlite3
import pandas as pd
import os

os.makedirs('data/processed', exist_ok=True)

def conectar():
    conexion = sqlite3.connect('data/processed/pipeline.db')
    return conexion

def crear_tablas(conexion):
    conexion.executescript("""
        DROP TABLE IF EXISTS ventas_raw;
        DROP TABLE IF EXISTS ventas_limpias;
        DROP TABLE IF EXISTS resumen_mensual;

        CREATE TABLE ventas_raw (
            id_pedido    INTEGER,
            fecha        TEXT,
            id_cliente   INTEGER,
            id_producto  INTEGER,
            categoria    TEXT,
            region       TEXT,
            segmento     TEXT,
            cantidad     INTEGER,
            precio_unit  REAL,
            descuento    REAL,
            ratio_costo  REAL
        );

        CREATE TABLE ventas_limpias (
            id_pedido     INTEGER PRIMARY KEY,
            fecha         TEXT,
            anio          INTEGER,
            mes           INTEGER,
            trimestre     INTEGER,
            id_cliente    INTEGER,
            id_producto   INTEGER,
            categoria     TEXT,
            region        TEXT,
            segmento      TEXT,
            cantidad      INTEGER,
            precio_unit   REAL,
            descuento     REAL,
            ratio_costo   REAL,
            ingreso       REAL,
            costo         REAL,
            ganancia      REAL,
            margen        REAL,
            tasa_impuesto REAL,
            ganancia_neta REAL,
            margen_neto   REAL,
            nivel_pedido  TEXT,
            es_atipico    INTEGER
        );

        CREATE TABLE resumen_mensual (
            anio          INTEGER,
            mes           INTEGER,
            trimestre     INTEGER,
            categoria     TEXT,
            region        TEXT,
            total_pedidos INTEGER,
            ingreso_total REAL,
            costo_total   REAL,
            ganancia_total REAL,
            margen_promedio REAL,
            PRIMARY KEY (anio, mes, categoria, region)
        );
    """)
    conexion.commit()
    print("Tablas creadas correctamente")

def cargar_csv(conexion):
    df = pd.read_csv('data/raw/ventas_raw.csv')
    df.to_sql('ventas_raw', conexion, if_exists='append', index=False)
    conexion.commit()
    total = conexion.execute("SELECT COUNT(*) FROM ventas_raw").fetchone()[0]
    print(f"ventas_raw cargada: {total} registros")

def extraer_con_sql(conexion):
    print("\n" + "="*50)
    print("FASE 1 — EXTRACCIÓN Y FILTRADO CON SQL")
    print("="*50)

    # Query 1: filtro básico con WHERE
    print("\nQ1 — Registros sin valores nulos (WHERE):")
    q1 = pd.read_sql_query("""
        SELECT *
        FROM ventas_raw
        WHERE precio_unit IS NOT NULL
          AND descuento IS NOT NULL
        ORDER BY fecha, id_pedido
    """, conexion)
    print(f"   Registros válidos: {len(q1)}")

    # Query 2: resumen por categoría con GROUP BY
    print("\n📌 Q2 — Resumen por categoría (GROUP BY):")
    q2 = pd.read_sql_query("""
        SELECT
            categoria,
            COUNT(*)                       AS total_pedidos,
            ROUND(AVG(precio_unit), 2)     AS precio_promedio,
            ROUND(AVG(descuento) * 100, 2) AS descuento_promedio_pct,
            SUM(cantidad)                  AS unidades_vendidas
        FROM ventas_raw
        WHERE precio_unit IS NOT NULL
        GROUP BY categoria
        ORDER BY total_pedidos DESC
    """, conexion)
    print(q2.to_string(index=False))

    # Query 3: clientes recurrentes con HAVING
    print("\n Q3 — Top clientes recurrentes (HAVING + subquery):")
    q3 = pd.read_sql_query("""
        SELECT
            id_cliente,
            COUNT(*)              AS num_pedidos,
            ROUND(AVG(precio_unit), 2) AS ticket_promedio
        FROM ventas_raw
        WHERE precio_unit IS NOT NULL
        GROUP BY id_cliente
        HAVING COUNT(*) >= 5
        ORDER BY num_pedidos DESC
        LIMIT 10
    """, conexion)
    print(q3.to_string(index=False))

    # Query 4: resumen por región con GROUP BY
    print("\n Q4 — Ventas por región (GROUP BY):")
    q4 = pd.read_sql_query("""
        SELECT
            region,
            segmento,
            COUNT(*)               AS pedidos,
            ROUND(AVG(precio_unit), 2) AS precio_promedio,
            SUM(cantidad)          AS unidades
        FROM ventas_raw
        WHERE precio_unit IS NOT NULL
          AND descuento IS NOT NULL
        GROUP BY region, segmento
        ORDER BY region, pedidos DESC
    """, conexion)
    print(q4.to_string(index=False))

    return q1

if __name__ == "__main__":
    conexion = conectar()
    crear_tablas(conexion)
    cargar_csv(conexion)
    extraer_con_sql(conexion)
    conexion.close()
    print("\nFase 1 completa — base de datos lista")