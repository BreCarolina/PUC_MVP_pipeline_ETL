
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

def carregar_dados(path_dados_transformados):
    if isinstance(path_dados_transformados, pd.DataFrame):
        return path_dados_transformados.copy()
    if not os.path.exists(path_dados_transformados):
        print(f"Arquivo não encontrado: {path_dados_transformados}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path_dados_transformados).dropna(how='all', axis=1)
        return df

    except Exception as e:
        print(f"[EXCEPTION] Erro ao carregar {path_dados_transformados}: {e}")
        return pd.DataFrame()

def obter_ultima_data(df):
    if 'data' in df.columns and not df.empty:
        ultima_data = pd.to_datetime(df['data'], errors='coerce').max()
        print(f"Última data registrada: {ultima_data}.")
        return ultima_data
    print("Nenhuma data existente nos dados antigos.")
    return None

def filtrar_novos_dados(df, ultima_data):
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    if ultima_data is not None:
        df_novo = df[df['data'] > ultima_data]
        print(f"Filtrando dados após {ultima_data}.\nNovos registros: {len(df_novo)}.")
        return df_novo
    print(f"\nTodos os dados serão transformados.\nRegistros: {len(df)}.")
    return df

def calcular_indicadores(df):
    try:
        df = df.sort_values(by=['data', 'hora']).copy()
        df['retorno'] = df['fechamento'].pct_change()

        df['SMA_10'] = df['fechamento'].rolling(window=10, min_periods=1).mean()
        df['EMA_10'] = df['fechamento'].ewm(span=10, min_periods=1).mean()

        ema_12 = df['fechamento'].ewm(span=12, min_periods=1).mean()
        ema_26 = df['fechamento'].ewm(span=26, min_periods=1).mean()
        df['MACD'] = ema_12 - ema_26
        df['Signal_Line'] = df['MACD'].ewm(span=9, min_periods=1).mean()

        ganho = df['retorno'].clip(lower=0)
        perda = -df['retorno'].clip(upper=0)
        media_ganho = ganho.ewm(span=14, min_periods=1).mean()
        media_perda = perda.ewm(span=14, min_periods=1).mean() + 1e-10
        df['rsi'] = 100 - (100 / (1 + media_ganho / media_perda))

        df['OBV'] = (df['volume'] * np.sign(df['fechamento'].diff().fillna(0))).cumsum()
        print("[OK] Indicadores calculados.")
    except Exception as e:
        print(f"[EXCEPTION] Erro ao calcular indicadores: {e}")
    return df

def adicionar_features_temporais(df):
    print("\nAdicionando features temporais...")
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df['dia_da_semana'] = df['data'].dt.dayofweek
        print("[OK] 'dia_da_semana' criado.")
    else:
        print("[ERRO] Coluna 'data' não encontrada.")

    if 'hora' in df.columns:
        hora = pd.to_datetime(df['hora'], format='%H:%M', errors='coerce')
        df['hora_num'] = hora.dt.hour.fillna(0).astype(int)
        df['minuto'] = hora.dt.minute.fillna(0).astype(int)
        print("[OK] 'hora_num' e 'minuto' criados.")
    else:
        df['hora_num'] = 0
        df['minuto'] = 0
        print("[ERRO] Coluna 'hora' não encontrada.")

    return df

def adicionar_features_diarias(df):
    try:
        print("Adicionando features diárias...")
        df['volume'] = df['volume'].fillna(0).astype(int)
        df = df.sort_values(by=['data', 'hora'])

        fechamento_dia = df.groupby('data').tail(1)[['data', 'fechamento']].set_index('data')['fechamento']
        df['fechamento_global'] = df['data'].map(fechamento_dia)
        df['volume_global'] = df.groupby('data')['volume'].transform('sum')
        df['maximo_global'] = df.groupby('data')['maximo'].transform('max')
        df['minimo_global'] = df.groupby('data')['minimo'].transform('min')

        df['fechamento_dia_anterior'] = df['fechamento_global'].shift(1)
        df['volume_dia_anterior'] = df['volume_global'].shift(1).fillna(0).astype(int)
        df['maximo_dia_anterior'] = df['maximo_global'].shift(1)
        df['minimo_dia_anterior'] = df['minimo_global'].shift(1)
        print("[OK] Features diárias adicionadas.")
    except Exception as e:
        print(f"[EXCEPTION] Erro ao adicionar features diárias: {e}")
    return df

def calcular_volatilidade(df, janela=20):
    try:
        df['retorno_log'] = np.log(df['fechamento'] / df['fechamento'].shift(1).replace(0, np.nan))
        df['volatilidade'] = df['retorno_log'].rolling(window=janela, min_periods=1).std()
        print("[OK] Volatilidade calculada.")
    except Exception as e:
        print(f"[EXCEPTION] Erro ao calcular volatilidade: {e}")
    return df

def substituir_nulos(df):
    colunas_para_media = ['retorno', 'retorno_log', 'SMA_10', 'EMA_10', 'MACD', 'Signal_Line', 'rsi', 'volatilidade']
    for col in colunas_para_media:
        if col in df.columns:
            media = df[col].mean(skipna=True)
            df[col] = df[col].fillna(media)
    return df

def transformar_dados(ticker, path_projeto):
    print('\nTransformação de dados...\n')

    path_dados_limpos = os.path.join(path_projeto, f'data/cleaned/dados_limpos_{ticker.split(".")[0]}.csv')
    path_dados_transformados = os.path.join(path_projeto, f'data/transformed/dados_transformados_{ticker.split(".")[0]}.csv')

    df_antigo = carregar_dados(path_dados_transformados)
    df_novo = carregar_dados(path_dados_limpos)
    df_novo = filtrar_novos_dados(df_novo, obter_ultima_data(df_antigo))

    if df_novo.empty:
        print("Nenhum novo dado para atualizar.")
        return df_antigo

    print("\nIniciando transformação...\n")
    for func in [
        calcular_indicadores,
        adicionar_features_temporais,
        adicionar_features_diarias,
        calcular_volatilidade
    ]:
        df_novo = func(df_novo)

    df_novo = substituir_nulos(df_novo)

    df_final = pd.concat([df_antigo, df_novo], ignore_index=True) if not df_antigo.empty else df_novo
    df_final.to_csv(path_dados_transformados, index=False)
    print(f"Dados transformados salvos em {path_dados_transformados}.\n({len(df_final)} registros).")
    return df_final
