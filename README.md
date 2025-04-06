# Análise de Séries Temporais e Detecção de Anomalias

Este projeto implementa uma análise de séries temporais para detecção de anomalias em processos operacionais, utilizando técnicas estatísticas e visualização de dados a partir de um arquivo CSV estruturado.

## Funcionalidades

- Carregamento e pré-processamento de dados de séries temporais (incluindo preenchimento de minutos ausentes).
- Geração de gráfico temporal com a evolução de múltiplos processos (CD_OPR).
- Cálculo de métricas estatísticas por processo:
    - Coeficiente de Variação (CV): Mede a variabilidade relativa da série.
    - Autocorrelação Máxima da Série Diferenciada: Identifica padrões periódicos ou de dependência temporal após remover tendências simples.
- Cálculo de um Score de Anomalia combinando as métricas.
- Detecção de anomalias usando Z-Score Robusto baseado na Mediana e no Desvio Absoluto Mediano (MAD).
- Análise da Função de Autocorrelação (ACF) para processos específicos, incluindo a série original e a diferenciada.
- Salvamento dos resultados da análise e dos gráficos gerados.

## Fórmula do Score de Anomalia

O score de anomalia é calculado da seguinte forma:

$$
\text{Score-anomaly} = \text{CV} \times \text{ACF}_\text{max}
$$

Onde:
- $CV$ (Coeficiente de Variação): `(desvio_padrão / média) * 100`. Mede a dispersão dos dados em relação à média. Valores altos indicam maior variabilidade relativa.
- $\text{ACF}_\text{max}$: Valor máximo da função de autocorrelação (ACF) calculada sobre a série temporal *diferenciada* (diferença entre valores consecutivos), ignorando o lag 0. Um valor alto sugere que, mesmo após remover a tendência de curto prazo (pela diferenciação), ainda existe uma estrutura de dependência temporal significativa (ex: sazonalidade, ciclos).

**Racional:** A multiplicação destas duas métricas visa destacar processos que são simultaneamente **muito variáveis** (CV alto) e que possuem **padrões temporais fortes** mesmo após a diferenciação (ACF alto). A hipótese é que tais processos são mais propensos a serem considerados "anômalos" ou, pelo menos, de interesse para investigação mais aprofundada em comparação com processos estáveis ou com variações puramente aleatórias.

A detecção final de anomalia utiliza um limiar baseado na mediana e no Median Absolute Deviation (MAD) dos scores calculados para todos os processos, tornando o método robusto a outliers nos próprios scores:

$$
\text{Limite Anomalia} = Mediana_ScoreAnomaly + 3 \times MAD_ScoreAnomaly
$$

Um processo é considerado anômalo se seu `score_anomaly` excede este limite.

## Estrutura do Projeto

```grapql
├── .gitignore
├── .python-version       # Define a versão Python (ex: 3.10.0)
├── README.md             # Este arquivo
├── data/
│   └── amostra.csv       # Dados de entrada
├── notebooks/            # (Opcional) Para exemplos e exploração
├── outputs/
│   ├── figures/          # Gráficos gerados (ACF, temporal)
│   └── resultados_anomalias.csv # Tabela com scores e classificação
├── poetry.lock
├── pyproject.toml        # Configuração do Poetry e dependências
├── src/
│   ├── __init__.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── acf.py        # Lógica para análise ACF
│   │   ├── anomaly.py    # Lógica principal de detecção de anomalias
│   │   └── metrics.py    # Funções para cálculo de métricas
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py     # Função para carregar e processar dados
│   └── visualization/
│       ├── __init__.py
│       └── plots.py      # Funções para gerar gráficos
└── tests/                # (Opcional) Testes unitários
    └── __init__.py
```

## Requisitos do Sistema

- Python (versão definida em `.python-version`, ex: 3.11.0)
- `pyenv` (recomendado para gerenciar versões do Python)
- `poetry` (para gerenciamento de dependências e ambiente virtual)

## Configuração do Ambiente

1.  **Clone o Repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO_GITHUB>
    cd <NOME_DO_DIRETORIO_CLONADO>
    ```

2.  **Instale a Versão Correta do Python com `pyenv`:**
    (Se você não tem o `pyenv`, instale-o primeiro: [https://github.com/pyenv/pyenv#installation](https://github.com/pyenv/pyenv#installation))
    ```bash
    # Instala a versão definida no .python-version (se ainda não instalada)
    pyenv install $(cat .python-version)
    # pyenv local $(cat .python-version) # Define a versão para este diretório (opcional)
    ```

3.  **Instale o Poetry:**
    (Se você não tem o Poetry, instale-o: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation))

4.  **Instale as Dependências do Projeto:**
    Este comando criará um ambiente virtual (se não existir) e instalará todos os pacotes listados no `pyproject.toml`.
    ```bash
    poetry install
    ```

## Como Usar

**Importante:** Execute todos os comandos a partir do diretório raiz do projeto.

1.  **Ative o Ambiente Virtual do Poetry (Opcional, mas recomendado):**
    ```bash
    poetry shell
    ```
    Se você ativar o shell, pode omitir `poetry run` dos comandos seguintes.

2.  **Execute a Análise Principal de Detecção de Anomalias:**
    ```bash
    poetry run python -m src.analysis.anomaly
    ```
    Isso irá:
    - Carregar os dados de `data/amostra.csv`.
    - Gerar o gráfico temporal geral em `outputs/figures/grafico_temporal_geral.png`.
    - Calcular métricas e o score de anomalia.
    - Imprimir os processos detectados como anômalos no console.
    - Salvar a tabela completa de resultados em `outputs/resultados_anomalias.csv`.

3.  **Execute a Análise ACF para Processos Específicos:**
    ```bash
    poetry run python -m src.analysis.acf
    ```
    Isso irá:
    - Iterar sobre a lista de `CD_OPR` definida no final de `src/analysis/acf.py`.
    - Para cada `CD_OPR`, gerar um gráfico ACF (Série, ACF Original, ACF Diferenciada) em `outputs/figures/acf_cd_opr_XXXXX.png`.
    - Imprimir as métricas ACF (máximo original e diferenciado) no console.


