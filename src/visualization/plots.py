"""
Módulo para visualização de dados.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
# A importação de plot_acf é feita dentro da função plot_acf_analysis
# para evitar dependência desnecessária se a função não for chamada.


def criar_grafico_temporal(dados, output_path='outputs/figures/grafico_temporal.png'):
    """
    Cria um gráfico temporal das séries dos diferentes processos.

    Args:
        dados (pd.DataFrame): DataFrame com os dados (colunas MINUTO, CD_OPR, QTD).
        output_path (str): Caminho para salvar o gráfico gerado.
    """
    if dados.empty:
        print("Aviso: DataFrame de entrada vazio. Gráfico temporal não gerado.")
        return

    try:
        # Pivoteia os dados
        dados_pivot = dados.pivot_table(
            index='MINUTO', columns='CD_OPR', values='QTD', fill_value=0)
    except Exception as e:
        print(f"Erro ao pivotear os dados para o gráfico: {e}")
        return

    # Criar gráfico temporal com os processos
    plt.figure(figsize=(12, 8))

    # Plotar cada coluna (CD_OPR) com uma cor diferente
    for coluna in dados_pivot.columns:
        plt.plot(dados_pivot.index,
                 dados_pivot[coluna], label=f'CD_OPR {coluna}')

    # Configurar o eixo X para exibir as datas de forma adequada
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    # Ajusta o locator dinamicamente baseado no range de tempo
    time_range_minutes = (dados['MINUTO'].max() -
                          dados['MINUTO'].min()).total_seconds() / 60
    if time_range_minutes <= 120:  # Menos de 2 horas
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
    elif time_range_minutes <= 1440:  # Menos de 1 dia
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    else:  # Mais de 1 dia
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    # Adicionar títulos e rótulos
    plt.title('Evolução temporal dos processos por minuto')
    plt.xlabel('Hora')
    plt.ylabel('Quantidade')
    plt.grid(True, linestyle='--', alpha=0.7)

    # Adicionar legenda
    plt.legend(title='Processos', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Ajustar layout
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Ajusta para caber a legenda fora

    # Rotacionar os rótulos do eixo X para melhor visualização
    plt.xticks(rotation=45)

    # Salvar e mostrar o gráfico
    try:
        plt.savefig(output_path)
        print(f"Gráfico temporal salvo em: {output_path}")
        # plt.show() # Comentar para não bloquear a execução em scripts
    except Exception as e:
        print(f"Erro ao salvar o gráfico temporal: {e}")
    finally:
        plt.close()  # Fecha a figura para liberar memória


def plot_acf_analysis(serie_temporal, datas, cd_opr_alvo, nlags=40, output_path='outputs/figures'):
    """
    Calcula e visualiza a série temporal e suas funções de autocorrelação (ACF).

    Args:
        serie_temporal (np.array): Array NumPy com os valores da série temporal.
        datas (pd.Series): Series Pandas com os timestamps correspondentes.
        cd_opr_alvo (str): O código do operador para incluir nos títulos.
        nlags (int): Número de lags para calcular na ACF.
        output_path (str): Diretório para salvar os gráficos.
    """
    from statsmodels.graphics.tsaplots import plot_acf

    if len(serie_temporal) < 2:
        print(
            f"Aviso: Série temporal para {cd_opr_alvo} muito curta para análise ACF.")
        return

    # Cria uma figura com três subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 15))

    # Subplot 1: Série temporal
    axes[0].plot(datas, serie_temporal)
    axes[0].set_title(f'Série Temporal - CD_OPR {cd_opr_alvo}')
    axes[0].set_xlabel('Tempo')
    axes[0].set_ylabel('Quantidade')
    axes[0].grid(True)

    # Subplot 2: ACF da série original
    try:
        plot_acf(serie_temporal, lags=nlags,
                 ax=axes[1], title=f'ACF - CD_OPR {cd_opr_alvo}')
    except Exception as e:
        print(f"Erro ao plotar ACF para {cd_opr_alvo}: {e}")

    # Subplot 3: ACF da série diferenciada
    try:
        serie_diff = np.diff(serie_temporal)
        plot_acf(serie_diff, lags=min(nlags, len(serie_diff)-1),
                 ax=axes[2], title=f'ACF da Série Diferenciada - CD_OPR {cd_opr_alvo}')
    except Exception as e:
        print(f"Erro ao plotar ACF diferenciada para {cd_opr_alvo}: {e}")

    # Ajusta o layout
    plt.tight_layout()

    # Salva o gráfico
    filename = f"{output_path}/acf_cd_opr_{cd_opr_alvo}.png"
    try:
        plt.savefig(filename)
        print(f"Gráfico ACF salvo em: {filename}")
    except Exception as e:
        print(f"Erro ao salvar o gráfico ACF para {cd_opr_alvo}: {e}")
    finally:
        plt.close()  # Fecha a figura
