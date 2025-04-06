# -*- coding: utf-8 -*-
"""
Módulo para carregamento e processamento de dados.
"""
import pandas as pd
import numpy as np


def extrair_dados(caminho):
    """
    Extrai dados do arquivo e retorna um DataFrame estruturado com todos os minutos preenchidos.

    Args:
        caminho (str): Caminho para o arquivo CSV.

    Returns:
        pd.DataFrame: DataFrame com os dados processados e completos.
    """
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {caminho}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return pd.DataFrame()

    # Filtra as linhas que contêm os dados
    dados_filtrados = [linha for linha in linhas if linha.startswith(
        'Insert into EXPORT_TABLE')]

    if not dados_filtrados:
        print("Aviso: Nenhuma linha de dados encontrada no formato esperado.")
        return pd.DataFrame()

    # Processa as linhas para extrair os valores
    dados_processados = []
    for linha in dados_filtrados:
        try:
            # Remove o prefixo e os caracteres desnecessários
            linha = linha.strip().replace(
                "Insert into EXPORT_TABLE (MINUTO,CD_OPR,QTD) values (", "").replace(");", "")
            partes = linha.split(',')
            if len(partes) == 3:
                dados_processados.append(partes)
            else:
                print(f"Aviso: Linha ignorada por formato inválido: {linha}")
        except Exception as e:
            print(f"Erro ao processar linha: {linha} - {e}")
            continue

    # Cria o DataFrame
    if not dados_processados:
        print("Aviso: Nenhum dado válido processado.")
        return pd.DataFrame()

    df = pd.DataFrame(dados_processados, columns=['MINUTO', 'CD_OPR', 'QTD'])

    try:
        # Remove aspas simples da coluna MINUTO
        df['MINUTO'] = df['MINUTO'].str.strip("'")

        # Converte a coluna MINUTO para datetime
        df['MINUTO'] = pd.to_datetime(df['MINUTO'], format='%Y-%m-%d %H:%M')

        # Converte a coluna QTD para inteiro
        df['QTD'] = df['QTD'].astype(int)
        # Garante que CD_OPR seja string
        df['CD_OPR'] = df['CD_OPR'].astype(str)
    except Exception as e:
        print(f"Erro ao converter tipos de dados: {e}")
        return pd.DataFrame()  # Retorna DF vazio em caso de erro de conversão

    # --- Preenchimento de minutos ausentes ---

    # Obtém a lista de todos os CD_OPR únicos
    cd_opr_unicos = df['CD_OPR'].unique()

    # Obtém o range completo de minutos (do início ao fim dos dados)
    min_time = df['MINUTO'].min()
    max_time = df['MINUTO'].max()
    # 'T' para frequência de minuto
    todos_minutos = pd.date_range(start=min_time, end=max_time, freq='T')

    # Cria um índice MultiIndex com todos os minutos e todos os CD_OPR
    novo_indice = pd.MultiIndex.from_product(
        [todos_minutos, cd_opr_unicos], names=['MINUTO', 'CD_OPR'])

    # Reindexa o DataFrame original com o novo índice completo
    # Define MINUTO e CD_OPR como índice para a operação de reindex
    df_indexed = df.set_index(['MINUTO', 'CD_OPR'])
    df_completo = df_indexed.reindex(novo_indice)

    # Preenche os valores ausentes de QTD com 0
    df_completo['QTD'] = df_completo['QTD'].fillna(0).astype(int)

    # Reseta o índice para ter MINUTO e CD_OPR como colunas novamente
    df_final = df_completo.reset_index()

    return df_final
