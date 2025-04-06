# -*- coding: utf-8 -*-
"""
Script principal para análise de séries temporais e detecção de anomalias.
"""
import pandas as pd
import numpy as np
import os
import sys

# Importações Relativas (necessárias para execução com python -m)
from ..data.loader import extrair_dados
from .metrics import calcula_cv, calcula_autocorr_diff, calcula_mad
from ..visualization.plots import criar_grafico_temporal

# Constantes
# O caminho relativo do script para as pastas data/ e outputs/ permanece o mesmo
CAMINHO_DADOS_PADRAO = os.path.join(
    os.path.dirname(__file__), '../../data/amostra.csv')
CAMINHO_OUTPUTS = os.path.join(
    os.path.dirname(__file__), '../../outputs')


def calcular_metricas_por_processo(dados):
    """
    Calcula as métricas estatísticas para cada processo (CD_OPR).

    Args:
        dados (pd.DataFrame): DataFrame completo com colunas MINUTO, CD_OPR, QTD.

    Returns:
        pd.DataFrame: DataFrame com as métricas calculadas por CD_OPR.
    """
    resultados = []

    # Garante que os dados estão ordenados por CD_OPR e MINUTO
    dados = dados.sort_values(['CD_OPR', 'MINUTO'])

    for cd_opr, grupo in dados.groupby('CD_OPR'):
        serie_temporal = grupo['QTD'].values

        # Pula séries muito pequenas para cálculo de métricas significativas
        if len(serie_temporal) < 10:
            print(
                f"Aviso: Série para CD_OPR {cd_opr} muito curta ({len(serie_temporal)} pontos), pulando cálculo de métricas.")
            continue

        # Calcula métricas usando funções do módulo metrics
        try:
            autocorr_max, autocorr_lag = calcula_autocorr_diff(serie_temporal)
            cv = calcula_cv(serie_temporal)

            resultados.append({
                'CD_OPR': cd_opr,
                'autocorr_max_diff': autocorr_max,
                'autocorr_lag': autocorr_lag,
                'cv': cv,
            })
        except Exception as e:
            print(f"Erro ao calcular métricas para CD_OPR {cd_opr}: {e}")
            continue  # Pula para o próximo CD_OPR em caso de erro

    if not resultados:
        return pd.DataFrame()  # Retorna DataFrame vazio se nenhuma métrica foi calculada

    return pd.DataFrame(resultados)


def detectar_anomalias(df_metricas, sigma_threshold=3):
    """
    Calcula um score de anomalia e identifica processos anormais
    usando Z-Score robusto baseado em MAD (Median Absolute Deviation).

    Args:
        df_metricas (pd.DataFrame): DataFrame com as métricas por CD_OPR.
        sigma_threshold (float): Número de desvios (MADs) para definir o limite.

    Returns:
        tuple: Contendo:
            - pd.DataFrame: DataFrame original com colunas 'score_anomaly' e 'anormal'.
            - float: Mediana do score de anomalia.
            - float: MAD do score de anomalia.
            - float: Limite superior de controle.
    """
    # Verifica se o DataFrame não está vazio e contém as colunas necessárias
    if df_metricas.empty or not all(col in df_metricas.columns for col in ['cv', 'autocorr_max_diff']):
        print("Aviso: DataFrame de métricas vazio ou faltando colunas. Não é possível detectar anomalias.")
        return pd.DataFrame(), np.nan, np.nan, np.nan

    # --- Cálculo do Score de Anomalia ---
    # Combina Coeficiente de Variação (CV) e Autocorrelação da Diferença
    # CV mede a variabilidade relativa
    # Autocorr da Diferença mede a presença de padrões após remover tendência simples
    # Multiplicação dá peso maior a séries que são *tanto* variáveis *quanto* com padrões na diferença
    df_metricas['score_anomaly'] = df_metricas['cv'] * \
        df_metricas['autocorr_max_diff']

    # Trata casos onde o score pode ser NaN ou Infinito (ex: cv infinito)
    df_metricas.replace([np.inf, -np.inf], np.nan, inplace=True)
    # Remove linhas onde o score não pôde ser calculado
    df_metricas.dropna(subset=['score_anomaly'], inplace=True)

    if df_metricas.empty:
        print("Aviso: Nenhum score de anomalia válido calculado.")
        return df_metricas, np.nan, np.nan, np.nan

    # --- Detecção de Anomalias com Z-Score Robusto (MAD) ---
    mediana = df_metricas['score_anomaly'].median()
    mad = calcula_mad(df_metricas['score_anomaly'])

    # Evita divisão por zero se MAD for 0 (todas as scores são iguais)
    if mad == 0:
        print("Aviso: MAD do score é zero. Anomalias não podem ser detectadas por este método.")
        # Marca todos como não anormais ou aplica outra lógica
        df_metricas['anormal'] = False
        limite_superior = mediana
    else:
        # Calcula o limite superior usando o threshold especificado
        limite_superior = mediana + sigma_threshold * mad
        # Identifica anomalias: score acima do limite superior
        df_metricas['anormal'] = df_metricas['score_anomaly'] > limite_superior

    # Ordena o DataFrame pelo score de anomalia em ordem decrescente
    df_metricas = df_metricas.sort_values('score_anomaly', ascending=False)

    return df_metricas, mediana, mad, limite_superior

# Função principal


def main(caminho_arquivo=CAMINHO_DADOS_PADRAO, caminho_outputs=CAMINHO_OUTPUTS):
    """
    Função principal que coordena a execução do programa.

    Args:
        caminho_arquivo (str): Caminho para o arquivo de dados.
        caminho_outputs (str): Caminho para a pasta de outputs.
    """
    print(f"Iniciando análise do arquivo: {caminho_arquivo}")

    # Garante que o diretório de output exista
    caminho_figuras = os.path.join(caminho_outputs, 'figures')
    os.makedirs(caminho_figuras, exist_ok=True)

    # Carrega os dados
    print("Carregando e processando dados...")
    dados = extrair_dados(caminho_arquivo)
    if dados.empty:
        print("Erro: Falha ao carregar os dados. Encerrando análise.")
        return
    print(f"Dados carregados: {len(dados)} registros.")

    # Cria o gráfico temporal geral
    print("Gerando gráfico temporal...")
    criar_grafico_temporal(dados, output_path=os.path.join(
        caminho_figuras, 'grafico_temporal_geral.png'))

    # Calcula métricas por processo
    print("Calculando métricas por processo...")
    df_metricas = calcular_metricas_por_processo(dados)
    if df_metricas.empty:
        print("Erro: Nenhuma métrica calculada. Encerrando análise.")
        return
    print("Métricas calculadas (primeiras 5 linhas):")
    print(df_metricas.head())

    # Detecta anomalias
    print("Detectando anomalias...")
    df_anomalias, mediana, mad, limite = detectar_anomalias(df_metricas)
    if df_anomalias.empty and np.isnan(mediana):
        print("Erro: Falha na detecção de anomalias.")
        return

    print("\n--- Estatísticas da Detecção de Anomalias ---")
    print(f"Mediana do Score: {mediana:.4f}")
    print(f"MAD do Score: {mad:.4f}")
    print(f"Limite Superior (Mediana + 3*MAD): {limite:.4f}")

    # Exibe resultados das anomalias
    print("\n=== PROCESSOS COM COMPORTAMENTO ANORMAL DETECTADO ===")
    anomalias_detectadas = df_anomalias[df_anomalias['anormal']]
    if anomalias_detectadas.empty:
        print("Nenhum processo com comportamento anormal foi detectado.")
    else:
        print(anomalias_detectadas)

    # Salva o dataframe com os scores e anomalias
    output_csv_path = os.path.join(caminho_outputs, 'resultados_anomalias.csv')
    try:
        df_anomalias.to_csv(output_csv_path, index=False)
        print(
            f"\nResultados da análise de anomalias salvos em: {output_csv_path}")
    except Exception as e:
        print(f"Erro ao salvar resultados em CSV: {e}")

    print("\nAnálise concluída.")


# Ponto de entrada do script
if __name__ == "__main__":
    # Você pode alterar o caminho do arquivo aqui se necessário
    # main(caminho_arquivo='caminho/para/seu/arquivo.csv')
    main()
