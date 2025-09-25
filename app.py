# Interaçao com o streamlit
import streamlit as st
import pandas as pd
import plotly.express as px
from modelo import prever_temperatura, prever_umidade
from sazonalidade import gerar_grafico_sazonal

st.set_page_config(page_title="Controle de Temperatura e Umidade", layout="wide")
st.title("🌡️💧 Monitoramento Inteligente - Estoque Seco")

# Configurable temperature thresholds for alerts.
# The upper threshold was set to 25°C based on recent storage guidelines (previously 22°C).
TEMP_MIN_THRESHOLD = 5
TEMP_MAX_THRESHOLD = 25

# 🔧 Padronização de colunas
def padronizar_colunas(df):
    colunas_limpa = []
    for col in df.columns:
        col = col.strip().lower().replace(" ", "_").replace("℃", "c").replace("%", "percent")
        col = col.replace("(", "").replace(")", "").replace(".", "")
        colunas_limpa.append(col)
    df.columns = colunas_limpa

    for col in df.columns:
        if "date" in col or "data" in col:
            df.rename(columns={col: "data"}, inplace=True)
        if "temperature" in col or "temperatura" in col or "temp" in col:
            df.rename(columns={col: "temperatura"}, inplace=True)
        if "humidity" in col:
            df.rename(columns={col: "umidade"}, inplace=True)
        if "dewpoint" in col:
            df.rename(columns={col: "ponto_orvalho"}, inplace=True)
        if "vpd" in col:
            df.rename(columns={col: "vpd"}, inplace=True)
    return df

# 📥 Leitura do CSV
try:
    df = pd.read_csv("dados/temperatura.csv", sep=";", encoding="latin1", skiprows=1)
except Exception as e:
    st.error("❌ Erro ao ler o arquivo CSV.")
    st.write(str(e))
    st.stop()

df = padronizar_colunas(df)

# 🗓️ Conversão de data
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df.dropna(subset=['data'], inplace=True)

# 🌡️ Conversão de temperatura
df['temperatura'] = pd.to_numeric(df.get('temperatura'), errors='coerce')
df.dropna(subset=['temperatura'], inplace=True)

# 💧 Conversão de umidade
df['umidade'] = pd.to_numeric(df.get('umidade'), errors='coerce')
df.dropna(subset=['umidade'], inplace=True)

# 🔔 Alertas
def alerta_temp(temp):
    if temp < TEMP_MIN_THRESHOLD:
        return "⚠️ Baixa"
    elif temp > TEMP_MAX_THRESHOLD:
        return "⚠️ Alta"
    else:
        return "✅ Ideal"

def alerta_umid(umid):
    return "✅ Ideal" if umid <= 70 else "⚠️ Inadequada"

df['alerta_temp'] = df['temperatura'].apply(alerta_temp)
df['alerta_umid'] = df['umidade'].apply(alerta_umid)

# 📅 Filtros de data com dia final completo
col1, col2 = st.columns(2)
inicio = col1.date_input("Data inicial", df['data'].min().date())
fim = col2.date_input("Data final", df['data'].max().date())
inicio_dt = pd.to_datetime(inicio)
fim_dt = pd.to_datetime(fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

df_filtrado = df[(df['data'] >= inicio_dt) & (df['data'] <= fim_dt)]

# 🔍 Diagnóstico do filtro
st.write("🔎 Intervalo selecionado:", inicio_dt, "→", fim_dt)
st.write("📊 Total de registros filtrados:", len(df_filtrado))

# 📋 Tabela interativa dos dados filtrados
st.subheader("📋 Tabela de Registros Filtrados")
st.dataframe(df_filtrado[['data', 'temperatura', 'umidade']].sort_values('data'))

# 📈 Gráfico de temperatura por registro
st.subheader("🌡️ Temperatura por Registro")
if not df_filtrado.empty:
    fig_temp = px.scatter(df_filtrado, x='data', y='temperatura', color='alerta_temp',
                          title='Temperatura por Registro', labels={'data': 'Data', 'temperatura': 'Temperatura (°C)'})
    fig_temp.update_traces(mode='markers+lines')
    fig_temp.update_xaxes(tickformat="%d %b %Hh")
    st.plotly_chart(fig_temp, use_container_width=True)
else:
    st.warning("Nenhum dado de temperatura disponível para o intervalo selecionado.")

# 📈 Gráfico de umidade por registro
st.subheader("💧 Umidade por Registro")
if not df_filtrado.empty:
    fig_umid = px.scatter(df_filtrado, x='data', y='umidade', color='alerta_umid',
                          title='Umidade por Registro', labels={'data': 'Data', 'umidade': 'Umidade (%)'})
    fig_umid.update_traces(mode='markers+lines')
    fig_umid.update_xaxes(tickformat="%d %b %Hh")
    st.plotly_chart(fig_umid, use_container_width=True)
else:
    st.warning("Nenhum dado de umidade disponível para o intervalo selecionado.")

# 🔮 Previsão de temperatura
st.subheader("🔮 Previsão de Temperatura")
dias = st.slider("Dias à frente", 1, 30, 7)
previsao_temp = prever_temperatura(df, dias)
st.line_chart(previsao_temp)

# 🔮 Previsão de Umidade
st.subheader("🔮 Previsão de Umidade")
previsao_umid = prever_umidade(df, dias)
st.line_chart(previsao_umid)

# 📊 Análise sazonal
st.subheader("📈 Análise Sazonal")
figs_sazonal = gerar_grafico_sazonal(df)
for fig in figs_sazonal:
    st.pyplot(fig)