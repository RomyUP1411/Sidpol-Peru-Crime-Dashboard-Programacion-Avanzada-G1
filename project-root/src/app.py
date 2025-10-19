import pandas as pd

# Leer el CSV
df = pd.read_csv(r"RomyUP1411/Sidpol-Peru-Crime-Dashboard-Programacion-Avanzada-G1/project-root/data/DATASET_Denuncias_Policiales_Enero 2018 a Setiembre 2025.csv")

# Mostrar primeras filas del Dataframe
print(df.head())
