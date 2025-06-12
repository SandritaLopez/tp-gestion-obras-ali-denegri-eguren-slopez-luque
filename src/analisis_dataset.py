import pandas as pd

df = pd.read_csv("./data/observatorio-de-obras-urbanas.csv", encoding="latin1", delimiter=";")         

print(df.head())
print(df.info())
print(df.isnull().sum())
