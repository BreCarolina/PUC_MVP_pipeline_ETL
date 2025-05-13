
import os
import logging
from PUC_MVP_pipeline_ETL.src.pipeline.extracao_dados import extrair_dados
from PUC_MVP_pipeline_ETL.src.pipeline.transformacao_dados import transformar_dados
from PUC_MVP_pipeline_ETL.src.pipeline.carga_dados import carregar_dados

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline_execucao.log"),
        logging.StreamHandler()
    ]
)

def main(ticker, path_projeto, intervalo):
    logging.info("Iniciando pipeline de dados...")

    # Caminhos dos arquivos (usados nos módulos internos se necessário)
    path_dados_brutos = os.path.join(path_projeto, f'data/raw/dados_brutos_{ticker.split(".")[0]}.csv')
    path_dados_limpos = os.path.join(path_projeto, f'data/cleaned/dados_limpos_{ticker.split(".")[0]}.csv')
    path_dados_transformados = os.path.join(path_projeto, f'data/transformed/dados_transformados_{ticker.split(".")[0]}.csv')
    path_sqlite = os.path.join(path_projeto, f'modelagem/database/SQLite_PUC_MVP_pipeline_ETL_{ticker.split(".")[0]}.db')

    # Extração
    df_extraido = extrair_dados(ticker, intervalo, path_projeto)
    if df_extraido is None or df_extraido.empty:
        logging.error("Falha na extração: nenhum dado retornado.")
        return

    # Transformação
    df_transformado = transformar_dados(ticker, path_projeto)
    if df_transformado is None or df_transformado.empty:
        logging.error("Falha na transformação: DataFrame transformado está vazio.")
        return

    # Carga
    carregar_dados(ticker, path_projeto)

    logging.info("Pipeline concluído com sucesso.")
    return df_transformado

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Executa o pipeline de dados B3")
    parser.add_argument("--ticker", required=True, help="Ticker do ativo (ex: PETR4.SA)")
    parser.add_argument("--path", required=True, help="Caminho base do projeto")
    parser.add_argument("--intervalo", required=True, help="Intervalo de coleta (ex: 5m, 15m)")

    args = parser.parse_args()
    main(args.ticker, args.path, args.intervalo)
