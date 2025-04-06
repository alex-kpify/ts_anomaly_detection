# -*- coding: utf-8 -*-
"""
Script para cálculo e visualização da Autocorrelação (ACF).
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

# --- Removendo o Hack sys.path ---
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.abspath(os.path.join(current_dir, '../../'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

# Importações Relativas (necessárias para execução com python -m)
from ..data.loader import extrair_dados
from .metrics import calcula_autocorr_diff  # Reutiliza a função
# Alternativamente: from .metrics import calcula_autocorr_diff
from ..visualization.plots import plot_acf_analysis  # Reutiliza a função de plot

# Constantes
# O caminho relativo do script para as pastas data/ e outputs/ permanece o mesmo
CAMINHO_DADOS_PADRAO = os.path.join(
    os.path.dirname(__file__), '../../data/amostra.csv')
CAMINHO_OUTPUTS = os.path.join(
    os.path.dirname(__file__), '../../outputs')


def analisar_acf_processo(cd_opr_alvo, caminho_arquivo=CAMINHO_DADOS_PADRAO,
                          caminho_outputs=CAMINHO_OUTPUTS, nlags=40, plot=True):
    """
    Realiza a análise ACF para um CD_OPR específico.

    Args:
        cd_opr_alvo (str): O código do operador para analisar.
        caminho_arquivo (str): Caminho para o arquivo de dados.
        caminho_outputs (str): Caminho para a pasta de outputs dos gráficos.
        nlags (int): Número de lags para calcular na ACF.
        plot (bool): Se True, gera e salva os gráficos ACF.
    """
    print(f"\n--- Análise ACF para CD_OPR: {cd_opr_alvo} ---")

    # Garante que o diretório de output exista
    os.makedirs(caminho_outputs, exist_ok=True)

    # Carrega os dados - loader.py já garante preenchimento com zeros
    dados = extrair_dados(caminho_arquivo)
    if dados.empty:
        print("Erro: Falha ao carregar dados para análise ACF.")
        return

    # Filtra os dados para o CD_OPR específico
    # Garante que a comparação seja string-string
    dados_filtrados = dados[dados['CD_OPR'] == str(cd_opr_alvo)]

    if dados_filtrados.empty:
        print(f"Não foram encontrados dados para o CD_OPR {cd_opr_alvo}")
        return

    # Ordena os dados por tempo (redundante se loader já faz, mas garante)
    dados_filtrados = dados_filtrados.sort_values('MINUTO')

    # Extrai a série temporal e as datas
    serie_temporal = dados_filtrados['QTD'].values
    datas = dados_filtrados['MINUTO']

    if len(serie_temporal) < 2:
        print(
            f"Série temporal para {cd_opr_alvo} muito curta ({len(serie_temporal)} pontos). Análise ACF não realizada.")
        return

    # --- Cálculo da ACF (usando statsmodels internamente no plot) ---
    # A função plot_acf_analysis já faz o cálculo e plotagem
    if plot:
        plot_acf_analysis(serie_temporal, datas, cd_opr_alvo,
                          nlags=nlags, output_path=caminho_outputs)

    # --- Cálculo e Exibição de Métricas ACF ---
    try:
        # Calcula ACF da série original para encontrar max_lag
        from statsmodels.tsa.stattools import acf  # Import local rápido
        valores_acf = acf(serie_temporal, nlags=min(
            nlags, len(serie_temporal)-1), fft=False)

        # Encontra o lag com valor máximo (excluindo lag 0)
        if len(valores_acf) > 1:
            acf_abs_orig = np.abs(valores_acf[1:])
            max_lag_orig = np.argmax(acf_abs_orig) + 1
            # Pega o valor real, não absoluto
            max_valor_orig = valores_acf[max_lag_orig]
            print(
                f"ACF Original Máxima: {max_valor_orig:.4f} no lag {max_lag_orig}")
        else:
            print("Não foi possível calcular ACF original (série muito curta).")

    except Exception as e:
        print(f"Erro ao calcular métricas ACF para série original: {e}")

    # Calcula ACF da série diferenciada usando a função de metrics
    try:
        max_acf_diff, max_lag_diff = calcula_autocorr_diff(
            serie_temporal, nlags=nlags)
        print(
            f"ACF Diferenciada Máxima (Abs): {max_acf_diff:.4f} no lag {max_lag_diff}")
    except Exception as e:
        print(f"Erro ao calcular métricas ACF para série diferenciada: {e}")


# Ponto de entrada do script
if __name__ == "__main__":
    # Lista de CD_OPR para analisar (pode ser lida de um arquivo ou argumento)
    lista_cd_opr = ["3290828", "199475",
                    "133830", "2585025", "3663749"]  # Exemplo

    print("Iniciando análise de Autocorrelação (ACF)...")
    for cd_opr in lista_cd_opr:
        analisar_acf_processo(cd_opr, plot=True)
        # Definir plot=False se não quiser gerar os gráficos para todos

    print("\nAnálise ACF concluída.")
