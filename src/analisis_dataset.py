import pandas as pd
import random

df = pd.read_csv("data/observatorio-de-obras-urbanas.csv", encoding="latin1", delimiter=";")         

print(df.head())
print(df.info())
print(df.isnull().sum())
print(df.columns)
# # print(df["tipo"].unique())
# # print(df["barrio"].unique())
# # print(df["area_responsable"].unique())
# print(df["contratacion_tipo"].unique())
# print(df["expediente-numero"].unique())
# print(df["licitacion_oferta_empresa"].unique())
# print(df["mano_obra"].unique())
print(df["destacada"].nunique())
print(df["destacada"].unique())
print(df["destacada"])
print(df["monto_contrato"])
print(df["expediente-numero"].dtype)
print(df["nro_contratacion"].dtype)
