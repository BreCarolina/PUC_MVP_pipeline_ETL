
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import logging

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

def limpeza_dados(df):
    print('\nIniciando limpeza de dados...\n')

    df.index = pd.to_datetime(df.index, utc=True)
    df.index = df.index.tz_convert("America/Sao_Paulo")
    df.index = df.index.tz_localize(None)

    df['hora'] = pd.to_datetime(df.index.strftime('%H:%M'))
    df.index.name = 'datetime'
    df = df.reset_index()
    df['data'] = pd.to_datetime(df['datetime'].dt.date, format='%Y-%m-%d')
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M').dt.time

    print("\nApós conversão de índice e criação das colunas hora e data:")
    print(df.head(4))

    mapeamento_colunas = {
        'Close': 'fechamento',
        'High': 'maximo',
        'Low': 'minimo',
        'Open': 'abertura',
        'Volume': 'volume'
    }

    df.rename(columns=mapeamento_colunas, inplace=True)

    for col in ['abertura', 'minimo', 'maximo', 'fechamento']:
        df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

    df['volume'] = pd.to_numeric(df['volume'], errors='coerce', downcast='integer')

    df = df[['data', 'hora', 'abertura', 'minimo', 'maximo', 'fechamento', 'volume', 'datetime']]

    print("\nApós reorganizar as colunas:")
    print(df.head(2))

    df = df.drop_duplicates(keep='first')
    df = df.dropna(thresh=df.shape[1] * 0.5)

    print("\nApós remover duplicatas e nulos:")
    print(df.head(2))

    df = df[df['data'].dt.weekday < 5]

    print("\nApós filtrar apenas os dias úteis:")
    print(df.head(2))

    df = df[(df['hora'] >= pd.to_datetime('09:55:00').time()) &
            (df['hora'] <= pd.to_datetime('18:05:00').time())]

    print("\nApós filtrar o intervalo de horário (09:55-18:05):")
    print(df.head(4))

    if df.empty:
        print("O DataFrame ficou vazio após o filtro de horário. Verifique se os dados estão dentro do intervalo de 09:55-18:05.")
    else:
        print("\nLimpeza de dados concluída com sucesso.\n")

    df_novo_limpo = df.sort_values(["data", "hora"], ascending=[True, True])
    print("\nDados limpos e ordenados:")
    print(df_novo_limpo.head(5))
    print(df_novo_limpo.tail(5))

    return df_novo_limpo

def extrair_dados(ticker, intervalo, path_projeto):
    print('\nExtração de dados...\n')

    path_dados_brutos = os.path.join(path_projeto, f'data/raw/dados_brutos_{ticker.split(".")[0]}.csv')
    path_dados_limpos = os.path.join(path_projeto, f'data/cleaned/dados_limpos_{ticker.split(".")[0]}.csv')

    df_total = pd.DataFrame()
    agora = datetime.now()
    hoje = agora.date()
    ontem = hoje - timedelta(days=1)

    # Define data_fim conforme horário e dia útil
    if agora.hour >= 17 and hoje.weekday() < 5:
        data_fim = hoje
    else:
        data_fim = ontem

    data_inicio = hoje - timedelta(days=58)
    primeira_extracao = True

    if os.path.exists(path_dados_limpos):
        df_existente = pd.read_csv(path_dados_limpos)
        df_existente["data"] = pd.to_datetime(df_existente["data"], format="%Y-%m-%d", errors="coerce")
        if "data" in df_existente.columns and pd.notnull(df_existente["data"].max()):
            ultimo_registro = pd.to_datetime(df_existente["data"]).max().date()
            print(f"Último registro encontrado: {ultimo_registro}")
            data_inicio = ultimo_registro + timedelta(days=1)
            primeira_extracao = False

    print(f"Extraindo dados de {data_inicio} até {data_fim}...")

    df_novo = yf.download(
        ticker,
        start=data_inicio.strftime("%Y-%m-%d"),
        end=(data_fim + timedelta(days=1)).strftime("%Y-%m-%d"),
        interval=intervalo,
        progress=False,
    )
    print(f"\nDados extraídos: {len(df_novo)} registros.")

    if not df_novo.empty:
        df_novo.columns = df_novo.columns.to_flat_index()
        df_novo.columns = [col[0] if isinstance(col, tuple) else col for col in df_novo.columns]

        df_novo_limpo = limpeza_dados(df_novo)

        if primeira_extracao:
            print("\nPrimeira extração de dados.")
            df_total_limpo = df_novo_limpo.copy()
            df_total_limpo.to_csv(path_dados_brutos, index=False)
            df_total_limpo.to_csv(path_dados_limpos, index=False)
            print(f"\nOs dados limpos foram armazenados em {path_dados_limpos}.")
        else:
            print("\nExtração complementar realizada.")
            df_total_limpo = pd.concat([df_existente, df_novo_limpo])
            df_total_limpo.drop_duplicates(subset=["datetime"], keep="first", inplace=True)
            df_total_limpo = df_total_limpo.sort_values(["data", "hora"])
            df_total_limpo.to_csv(path_dados_limpos, index=False)
            print("\nOs dados complementares foram salvos em CSV.")

        return df_total_limpo
    else:
        print("\nNenhum dado complementar foi adicionado.")
        if primeira_extracao:
            return pd.DataFrame()
        else:
            return df_existente if 'df_existente' in locals() and not df_existente.empty else pd.DataFrame()


