
import os
import logging
import PySimpleGUI as sg
from PUC_MVP_pipeline_ETL.src.pipeline.extracao_dados import extrair_dados
from PUC_MVP_pipeline_ETL.src.pipeline.transformacao_dados import transformar_dados
from PUC_MVP_pipeline_ETL.src.pipeline.carga_dados import carregar_dados

# Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline_execucao.log"),
        logging.StreamHandler()
    ]
)

INTERVALOS_VALIDOS = ['1d', '5m', '15m', '30m', '1h', '1wk']

def main(ticker, path_projeto, intervalo):
    logging.info(f"Pipeline iniciado para {ticker} com intervalo {intervalo}")

    if intervalo not in INTERVALOS_VALIDOS:
        logging.error(f"Intervalo inválido: {intervalo}")
        sg.popup_error(f"❌ Intervalo inválido. Use: {', '.join(INTERVALOS_VALIDOS)}")
        return

    if not os.path.isdir(path_projeto):
        logging.error(f"Caminho inexistente: {path_projeto}")
        sg.popup_error("❌ Caminho do projeto inválido.")
        return

    try:
        df_extraido = extrair_dados(ticker, intervalo, path_projeto)
        if df_extraido is None or df_extraido.empty:
            raise ValueError("Nenhum dado extraído.")
    except Exception as e:
        logging.exception("Erro na etapa de extração")
        sg.popup_error(f"Erro na extração: {e}")
        return

    try:
        df_transformado = transformar_dados(ticker, path_projeto)
        if df_transformado is None or df_transformado.empty:
            raise ValueError("DataFrame transformado está vazio.")
    except Exception as e:
        logging.exception("Erro na etapa de transformação")
        sg.popup_error(f"Erro na transformação: {e}")
        return

    try:
        carregar_dados(ticker, path_projeto)
    except Exception as e:
        logging.exception("Erro na etapa de carga")
        sg.popup_error(f"Erro na carga: {e}")
        return

    logging.info("Pipeline concluído com sucesso.")
    sg.popup("✅ Pipeline concluído com sucesso!")

def mostrar_interface():
    sg.theme('SystemDefault')

    layout = [
        [sg.Text("Ticker (ex: PETR4.SA):"), sg.InputText(key='TICKER')],
        [sg.Text("Caminho do Projeto:"), sg.InputText(key='PATH'), sg.FolderBrowse()],
        [sg.Text("Intervalo (ex: 1d, 5m):"), sg.InputText(key='INTERVALO')],
        [sg.Button("Executar"), sg.Button("Cancelar")]
    ]

    window = sg.Window("Executar Pipeline ETL", layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancelar"):
            break
        if event == "Executar":
            ticker = values['TICKER'].strip()
            path = values['PATH'].strip()
            intervalo = values['INTERVALO'].strip()

            if not ticker or not path or not intervalo:
                sg.popup_error("❌ Todos os campos são obrigatórios.")
                continue

            window.close()
            main(ticker, path, intervalo)
            break

    window.close()

if __name__ == "__main__":
    mostrar_interface()
