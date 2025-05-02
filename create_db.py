import pandas as pd
import sqlite3

# Cargar el archivo Excel
df = pd.read_excel("Raw_Data_Q1_2024_and_Q1_2025.xlsx", sheet_name="Sheet1")

# Guardar en base de datos SQLite
conn = sqlite3.connect("data.db")
df.to_sql("campaigns", conn, if_exists="replace", index=False)
conn.close()

print("Base de datos creada exitosamente como 'data.db'")
