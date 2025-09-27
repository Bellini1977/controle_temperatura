# Previsão com machine learning
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

# Previsão de temperatura
def prever_temperatura(df, dias):
    if 'data' not in df.columns or 'temperatura' not in df.columns:
        raise ValueError("Colunas 'data' e 'temperatura' são obrigatórias.")

    df['dia'] = df['data'].dt.dayofyear
    X = df[['dia']]
    y = df['temperatura']

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X, y)

    datas_futuras = [df['data'].max() + pd.Timedelta(days=i) for i in range(1, dias + 1)]
    dias_futuros = pd.DataFrame({'dia': [d.dayofyear for d in datas_futuras]})
    previsoes = modelo.predict(dias_futuros)

    return pd.Series(previsoes, index=datas_futuras)

# Previsão de umidade
def prever_umidade(df, dias):
    if 'data' not in df.columns or 'umidade' not in df.columns:
        raise ValueError("Colunas 'data' e 'umidade' são obrigatórias.")

    df['dia'] = df['data'].dt.dayofyear
    X = df[['dia']]
    y = df['umidade']

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X, y)

    datas_futuras = [df['data'].max() + pd.Timedelta(days=i) for i in range(1, dias + 1)]
    dias_futuros = pd.DataFrame({'dia': [d.dayofyear for d in datas_futuras]})
    previsoes = modelo.predict(dias_futuros)

    return pd.Series(previsoes, index=datas_futuras)