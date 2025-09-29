## Interaçao com o streamlit
# Interaçao com o streamlit
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import plotly.express as px
from modelo import prever_temperatura, prever_umidade
from sazonalidade import gerar_grafico_sazonal

st.set_page_config(page_title="Controle de Temperatura e Umidade", layout="wide")
st.title("🌡️💧 Monitoramento Inteligente - Estoque Seco")

TEMP_MIN_THRESHOLD = 5
TEMP_MAX_THRESHOLD = 25

# Padronização de colunas
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

# Leitura do CSV
try:
    df = pd.read_csv("dados/temperatura.csv", sep=";", encoding="latin1", skiprows=1)
    df = df.applymap(lambda x: str(x).replace(",", ".") if isinstance(x, str) else x)
except Exception as e:
    st.error("❌ Erro ao ler o arquivo CSV.")
    st.write(str(e))
    st.stop()

df = padronizar_colunas(df)

# Conversão de data
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df.dropna(subset=['data'], inplace=True)

# Conversão de temperatura
df['temperatura'] = pd.to_numeric(df.get('temperatura'), errors='coerce')
df.dropna(subset=['temperatura'], inplace=True)

# Conversão de umidade
df['umidade'] = pd.to_numeric(df.get('umidade'), errors='coerce')
df.dropna(subset=['umidade'], inplace=True)

# Alertas
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

# Filtros de data com dia final completo
col1, col2 = st.columns(2)
inicio = col1.date_input("Data inicial", df['data'].min().date())
fim = col2.date_input("Data final", df['data'].max().date())
inicio_dt = pd.to_datetime(inicio)
fim_dt = pd.to_datetime(fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

df_filtrado = df[(df['data'] >= inicio_dt) & (df['data'] <= fim_dt)]

# 🔍 Diagnóstico do filtro
st.write("🔎 Intervalo selecionado:", inicio_dt, "→", fim_dt)
st.write("📊 Total de registros filtrados:", len(df_filtrado))

# Dia mais quente e mais úmido
if not df_filtrado.empty:
    dia_quente = df_filtrado.loc[df_filtrado['temperatura'].idxmax()]['data'].strftime('%d/%m/%Y %H:%M')
    dia_umido = df_filtrado.loc[df_filtrado['umidade'].idxmax()]['data'].strftime('%d/%m/%Y %H:%M')
    st.markdown(f"🔥 **Dia mais quente:** {dia_quente}")
    st.markdown(f"💧 **Dia mais úmido:** {dia_umido}")

# Tabela interativa dos dados filtrados
st.subheader("📋 Tabela de Registros Filtrados")
st.dataframe(df_filtrado[['data', 'temperatura', 'umidade']].sort_values('data'))

# Gráfico de temperatura por registro (linha única com cores diferentes)
st.subheader("🌡️ Temperatura por Registro")
if not df_filtrado.empty:
    # Dicionário de cores
    cores = {
        "⚠️ Alta": "red",
        "⚠️ Baixa": "blue",
        "✅ Ideal": "green"
    }

    fig_temp = go.Figure()

    # Adiciona a linha contínua (sem categorias)
    fig_temp.add_trace(go.Scatter(
        x=df_filtrado["data"],
        y=df_filtrado["temperatura"],
        mode="lines",
        line=dict(color="lightgray", width=2),
        name="Temperatura"
    ))

    # Adiciona os pontos coloridos pela categoria
    for alerta, cor in cores.items():
        df_temp = df_filtrado[df_filtrado["alerta_temp"] == alerta]
        fig_temp.add_trace(go.Scatter(
            x=df_temp["data"],
            y=df_temp["temperatura"],
            mode="markers",
            marker=dict(color=cor, size=8),
            name=alerta,
            hovertemplate="Data: %{x}<br>Temp: %{y}°C<br>Status: " + alerta
        ))

    fig_temp.update_layout(
        title="Temperatura por Registro",
        xaxis_title="Data",
        yaxis_title="Temperatura (°C)",
        xaxis=dict(tickformat="%d %b %Hh"),
        legend=dict(title="Legenda")
    )

    st.plotly_chart(fig_temp, use_container_width=True)
else:
    st.warning("Nenhum dado de temperatura disponível para o intervalo selecionado.")



# Gráfico de umidade por registro
st.subheader("💧 Umidade por Registro")
if not df_filtrado.empty:
    fig_umid = px.scatter(df_filtrado, x='data', y='umidade', color='alerta_umid',
                          title='Umidade por Registro', labels={'data': 'Data', 'umidade': 'Umidade (%)'})
    fig_umid.update_traces(mode='markers+lines')
    fig_umid.update_xaxes(tickformat="%d %b %Hh")
    st.plotly_chart(fig_umid, use_container_width=True)
else:
    st.warning("Nenhum dado de umidade disponível para o intervalo selecionado.")

# Previsão de temperatura
st.subheader("🔮 Previsão de Temperatura")
dias = st.slider("Dias à frente", 1, 30, 7)
previsao_temp = prever_temperatura(df, dias)
st.line_chart(previsao_temp)

# Previsão de Umidade
st.subheader("🔮 Previsão de Umidade")
previsao_umid = prever_umidade(df, dias)
st.line_chart(previsao_umid)

# Análise sazonal
st.subheader("📈 Análise Sazonal")
figs_sazonal = gerar_grafico_sazonal(df)
for fig in figs_sazonal:
    st.pyplot(fig)