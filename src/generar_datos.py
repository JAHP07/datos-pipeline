import pandas as pd
import numpy as np
import random
import datetime
import os

random.seed(42)
np.random.seed(42)

categorias = ['Electrónica', 'Ropa', 'Alimentos', 'Libros', 'Deportes', 'Hogar', 'Belleza']
regiones   = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
segmentos  = ['Retail', 'Mayorista', 'Online', 'Corporativo']

cantidad = 5000
fecha_inicio = datetime.date(2023, 1, 1)
fechas = [fecha_inicio + datetime.timedelta(days=random.randint(0, 365)) for _ in range(cantidad)]

df = pd.DataFrame({
    'id_pedido':    range(1001, 1001 + cantidad),
    'fecha':        fechas,
    'id_cliente':   np.random.randint(100, 800, cantidad),
    'id_producto':  np.random.randint(2000, 2500, cantidad),
    'categoria':    np.random.choice(categorias, cantidad),
    'region':       np.random.choice(regiones, cantidad),
    'segmento':     np.random.choice(segmentos, cantidad),
    'cantidad':     np.random.randint(1, 20, cantidad),
    'precio_unit':  np.round(np.random.uniform(5, 500, cantidad), 2),
    'descuento':    np.round(np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.25], cantidad), 2),
    'ratio_costo':  np.round(np.random.uniform(0.4, 0.75, cantidad), 3),
})

# Inyectar problemas de calidad para practicar limpieza
indices_nulos = random.sample(range(cantidad), 200)
df.loc[indices_nulos[:100], 'precio_unit'] = None
df.loc[indices_nulos[100:], 'descuento']   = None

# Inyectar duplicados
indices_dup = random.sample(range(cantidad), 50)
df = pd.concat([df, df.iloc[indices_dup]], ignore_index=True)

os.makedirs('data/raw', exist_ok=True)
df.to_csv('data/raw/ventas_raw.csv', index=False)

print(f"Dataset creado: {df.shape[0]} filas x {df.shape[1]} columnas")
print(f"\nNulos por columna:")
print(df.isnull().sum())
print(f"\nPrimeras 3 filas:")
print(df.head(3).to_string())