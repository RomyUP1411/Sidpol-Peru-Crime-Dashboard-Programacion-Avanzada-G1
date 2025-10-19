import pandas as pd

# Leer CSV
df = pd.read_csv(r"project-root\data\DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv")

# Mostrar las primeras filas del DataFrame
print(df.head())
