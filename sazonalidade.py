# Análise temporal
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

def gerar_grafico_sazonal(df):
    if 'data' not in df.columns:
        raise ValueError("Coluna 'data' é obrigatória.")
    if 'temperatura' not in df.columns and 'umidade' not in df.columns:
        raise ValueError("É necessário ter pelo menos uma das colunas: 'temperatura' ou 'umidade'.")

    fig_list = []

    if 'temperatura' in df.columns:
        df_temp = df.set_index('data')['temperatura'].asfreq('D').fillna(method='ffill')
        if len(df_temp) >= 14:
            resultado_temp = seasonal_decompose(df_temp, model='additive')
            fig_temp, ax_temp = plt.subplots(4, 1, figsize=(10, 8))
            resultado_temp.observed.plot(ax=ax_temp[0], title='Temperatura Observada')
            resultado_temp.trend.plot(ax=ax_temp[1], title='Tendência da Temperatura')
            resultado_temp.seasonal.plot(ax=ax_temp[2], title='Sazonalidade da Temperatura')
            resultado_temp.resid.plot(ax=ax_temp[3], title='Resíduo da Temperatura')
            plt.tight_layout()
            fig_list.append(fig_temp)
        else:
            fig_temp, ax_temp = plt.subplots()
            ax_temp.text(0.5, 0.5, "Dados insuficientes para análise sazonal da temperatura (mínimo: 14 dias)",
                         ha='center', va='center', fontsize=12)
            ax_temp.axis('off')
            fig_list.append(fig_temp)

    if 'umidade' in df.columns:
        df_umid = df.set_index('data')['umidade'].asfreq('D').fillna(method='ffill')
        if len(df_umid) >= 14:
            resultado_umid = seasonal_decompose(df_umid, model='additive')
            fig_umid, ax_umid = plt.subplots(4, 1, figsize=(10, 8))
            resultado_umid.observed.plot(ax=ax_umid[0], title='Umidade Observada')
            resultado_umid.trend.plot(ax=ax_umid[1], title='Tendência da Umidade')
            resultado_umid.seasonal.plot(ax=ax_umid[2], title='Sazonalidade da Umidade')
            resultado_umid.resid.plot(ax=ax_umid[3], title='Resíduo da Umidade')
            plt.tight_layout()
            fig_list.append(fig_umid)
        else:
            fig_umid, ax_umid = plt.subplots()
            ax_umid.text(0.5, 0.5, "Dados insuficientes para análise sazonal da umidade (mínimo: 14 dias)",
                         ha='center', va='center', fontsize=12)
            ax_umid.axis('off')
            fig_list.append(fig_umid)

    return fig_list