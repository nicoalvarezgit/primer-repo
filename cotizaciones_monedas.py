# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 12:42:48 2024

@author: L12504
"""

import requests
import pandas as pd
from datetime import datetime, timedelta

# Lista de códigos de las monedas (ejemplo: USD, EUR, etc.)
monedas = ["USD", "EUR", "CHF", "GBP", "JPY", "BRL", "CAD", "CNH", "UYU", "XDR"]

# Fechas de consulta
fecha_desde = "2021-01-01"
fecha_hasta = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # El día anterior a la fecha actual

# Diccionario para almacenar los resultados de cada moneda
cotizaciones = {}

# Iterar sobre cada moneda y hacer la solicitud
for moneda in monedas:
    url = f"https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/{moneda}?fechadesde={fecha_desde}&fechahasta={fecha_hasta}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        cotizaciones[moneda] = data  # Guardar los datos de la moneda
        print(f"Cotizaciones de {moneda}: {data}")
    else:
        print(f"Error al consultar {moneda}: {response.status_code}")

# Ahora tienes las cotizaciones en el diccionario 'cotizaciones' para cada moneda

# Inicializar un diccionario para construir el DataFrame
datos_cotizaciones = {}

# Iterar sobre cada moneda en el diccionario 'cotizaciones'
for moneda, data in cotizaciones.items():
    # Extraer las fechas y los tipos de cambio de cada moneda
    fechas = []
    tipos_cambio = []
    
    # Acceder a la lista de cotizaciones por fecha
    for entry in data['results']:
        fechas.append(entry['fecha'])
        tipos_cambio.append(entry['detalle'][0]['tipoCotizacion'])
    
    # Agregar los datos al diccionario, usando la moneda como clave
    datos_cotizaciones[moneda] = pd.Series(tipos_cambio, index=fechas)

# Convertir el diccionario en un DataFrame
df_cotizaciones = pd.DataFrame(datos_cotizaciones)

# Renombrar la columna "REF" a "USD"
df_cotizaciones.rename(columns={"REF": "USD"}, inplace=True)

# Renombrar la columna "XDR" a "DEG"
df_cotizaciones.rename(columns={"XDR": "DEG"}, inplace=True)

# Convertir el índice a formato datetime para usarlo en el resampleo
df_cotizaciones.index = pd.to_datetime(df_cotizaciones.index)

# Calcular el promedio mensual
df_mensual = df_cotizaciones.resample('M').mean()

ruta_excel = "C:/Users/l12504/BCRA/Vigilancia - Documentos/General/Vigilancia/DATOS/3_REPOSITORIO_DE_DATOS/cotizaciones_monedas.xlsx"

# Guardar el archivo Excel con las dos hojas
with pd.ExcelWriter(ruta_excel, engine='xlsxwriter') as writer:
    # Escribir la hoja de cotizaciones diarias
    df_cotizaciones.to_excel(writer, sheet_name='cotizaciones diarias')
    
    # Escribir la hoja de cotizaciones mensuales
    df_mensual.to_excel(writer, sheet_name='cotizaciones mensuales')

print("Archivo Excel generado correctamente.")
