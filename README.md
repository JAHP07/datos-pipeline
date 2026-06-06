# datos-pipeline

Proyecto para análisis y transformación de datos orientado a generar informes y visualizaciones reproducibles.

## Historia

Este repositorio nació como ejercicio para construir una canalización de datos simple que:
- Ingesta datos desde SQLite
- Ejecuta transformaciones y análisis descriptivo
- Genera gráficos EDA para facilitar la interpretación

A lo largo del tiempo se añadieron scripts para automatizar el EDA y emitir reportes visuales que soporten decisiones analíticas.

## Arquitectura

La arquitectura es intencionalmente simple y modular:

- src/: Código fuente principal
  - src/analisis.py — Script principal de análisis y generación de gráficos (EDA)
  - src/utils.py — Utilidades compartidas (si aplica)
- data/: Ubicación esperada para orígenes de datos (no versionado)
- reports/: Salida de reportes y gráficos
  - reports/plots/ — Gráficos PNG generados por analisis.py
- README.md — Documentación del proyecto

Flujo de trabajo:
1. Extraer datos desde la fuente (SQLite por defecto)
2. Ejecutar src/analisis.py para producir estadísticas y gráficos
3. Versionar los artefactos relevantes (scripts y resúmenes); los gráficos se pueden versionar si procede

## Gráficos generados (ejemplo)
Los siguientes gráficos se generan actualmente y se guardan en reports/plots/:
- 01_distribuciones.png — Distribuciones univariantes de las variables clave
- 02_ingreso_categoria.png — Ingreso por categoría
- 03_serie_temporal.png — Serie temporal de métricas agregadas
- 04_correlaciones.png — Matriz de correlaciones
- 05_boxplot.png — Boxplots por categoría
- 06_dispersion.png — Scatter plots para pares seleccionados
- 07_region_categoria.png — Comparaciones por región y categoría

## Cómo ejecutar el análisis y regenerar gráficos

1. Asegurarse de tener las dependencias (recomendado crear un entorno virtual):

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt  # si existe

2. Ejecutar el script de análisis:

   python src/analisis.py

Los gráficos se guardarán en reports/plots/. Revisa logs en consola para mensajes y estadísticas descriptivas.

## Buenas prácticas
- No versionar datos sensibles ni grandes binarios; si necesitas versionar artefactos, considera usar un tag o release.
- Mantener el código de análisis reproducible: registrar versiones de dependencias y semilla aleatoria cuando aplique.

## Contribuir
1. Abrir un issue describiendo la propuesta
2. Crear una rama con el prefijo feat/ o fix/
3. Hacer un PR con descripción clara del cambio

## Licencia
Este repositorio no especifica una licencia por defecto. Añadir LICENSE si se requiere uso público.


