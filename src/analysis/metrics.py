# -*- coding: utf-8 -*-
"""
Módulo para cálculo de métricas estatísticas de séries temporais.
"""
import numpy as np
from statsmodels.tsa.stattools import acf
from statsmodels import robust  # Para MAD


def calcula_cv(serie):
    """Calcula o coeficiente de variação da série."""
    mean = serie.mean()
    std = serie.std()
    if mean == 0:
        return np.inf  # Ou 0, dependendo da interpretação desejada para CV de série zero
    return (std / mean) * 100


def calcula_autocorr_diff(serie, nlags=360):
    """
    Calcula a autocorrelação máxima da série diferenciada.

    Retorna o valor absoluto máximo da ACF (ignorando lag 0) e o lag correspondente.
    Retorna (0, 0) se a série for muito curta ou constante após diferenciação.
    """
    if len(serie) < 2:
        return 0, 0  # Não pode diferenciar

    diff_serie = np.diff(serie)

    if len(diff_serie) < 2 or np.all(diff_serie == diff_serie[0]):
        # Série constante após diferenciação ou muito curta
        return 0, 0

    try:
        # fft=False pode ser mais estável para algumas séries
        acf_diff = acf(diff_serie, nlags=min(
            nlags, len(diff_serie)-1), fft=False)

        # Ignora o lag 0
        acf_abs = np.abs(acf_diff[1:])
        if len(acf_abs) == 0:
            return 0, 0

        max_value = np.max(acf_abs)
        max_lag = np.argmax(acf_abs) + 1  # +1 porque ignoramos o lag 0

        return max_value, max_lag

    except Exception as e:
        print(f"Erro ao calcular ACF da série diferenciada: {e}")
        return 0, 0  # Retorna 0 em caso de erro


def calcula_mad(serie):
    """Calcula o Median Absolute Deviation (MAD)."""
    return robust.mad(serie)
