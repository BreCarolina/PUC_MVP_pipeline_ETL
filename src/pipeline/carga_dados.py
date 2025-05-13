
import sqlite3
import pandas as pd
from datetime import datetime
import os

def conectar_db(caminho_db):
    return sqlite3.connect(caminho_db)

def criar_tabelas(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_tempo (
        id_tempo INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        hora TEXT NOT NULL,
        dia_da_semana INTEGER NOT NULL,
        UNIQUE(data, hora)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_indicadores (
        id_indicadores INTEGER PRIMARY KEY AUTOINCREMENT,
        SMA_10 REAL, EMA_10 REAL, MACD REAL, Signal_Line REAL,
        rsi REAL, OBV REAL, retorno_log REAL, volatilidade REAL,
        volume INTEGER, volume_global INTEGER,
        UNIQUE(SMA_10, EMA_10, MACD, Signal_Line, rsi, OBV, retorno_log, volatilidade, volume, volume_global)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_agregados (
        id_agregados INTEGER PRIMARY KEY AUTOINCREMENT,
        hora_num INTEGER, minuto INTEGER,
        fechamento_dia_anterior REAL, volume_dia_anterior INTEGER,
        maximo_dia_anterior REAL, minimo_dia_anterior REAL,
        UNIQUE(hora_num, minuto, fechamento_dia_anterior, volume_dia_anterior, maximo_dia_anterior, minimo_dia_anterior)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fato_precos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        abertura REAL, minima REAL, maxima REAL, fechamento REAL,
        abertura_global REAL, minima_global REAL, maxima_global REAL, fechamento_global REAL,
        id_tempo INTEGER, id_indicadores INTEGER, id_agregados INTEGER,
        FOREIGN KEY (id_tempo) REFERENCES dim_tempo(id_tempo),
        FOREIGN KEY (id_indicadores) REFERENCES dim_indicadores(id_indicadores),
        FOREIGN KEY (id_agregados) REFERENCES dim_agregados(id_agregados),
        UNIQUE(id_tempo, id_indicadores, id_agregados)
    );
    """)

    conn.commit()

def obter_id(conn, tabela, valores):
    df = pd.DataFrame([valores])
    placeholders = ','.join(['?'] * len(valores))
    colunas = ','.join(valores.keys())
    cursor = conn.cursor()

    query = f"SELECT rowid FROM {tabela} WHERE " + ' AND '.join([f"{k}=?" for k in valores])
    cursor.execute(query, tuple(valores.values()))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})", tuple(valores.values()))
    conn.commit()
    return cursor.lastrowid

def dados_ja_inseridos(conn, data, hora):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM dim_tempo WHERE data = ? AND hora = ?", (data, hora))
    return cursor.fetchone() is not None

def carregar_dados(ticker, path_projeto):
    print('\nIniciando a carga de dados...')

    caminho_csv = os.path.join(path_projeto, f'data/transformed/dados_transformados_{ticker.split(".")[0]}.csv')
    caminho_db = os.path.join(path_projeto, f'modelagem/database/SQLite_{ticker.split(".")[0]}.db')

    # Garante que a pasta do banco existe
    os.makedirs(os.path.dirname(caminho_db), exist_ok=True)

    if not os.path.exists(caminho_csv):
        print(f"[ERRO] Arquivo CSV não encontrado: {caminho_csv}")
        return

    df = pd.read_csv(caminho_csv)

    if df.empty:
        print("[INFO] Nenhum dado para inserir.")
        return

    conn = conectar_db(caminho_db)
    criar_tabelas(conn)

    novos_registros = 0
    for _, row in df.iterrows():
        data = row['data']
        hora = row['hora']

        if dados_ja_inseridos(conn, data, hora):
            continue

        id_tempo = obter_id(conn, 'dim_tempo', {
            'data': data,
            'hora': hora,
            'dia_da_semana': row['dia_da_semana']
        })

        id_ind = obter_id(conn, 'dim_indicadores', {
            'SMA_10': row['SMA_10'], 'EMA_10': row['EMA_10'],
            'MACD': row['MACD'], 'Signal_Line': row['Signal_Line'],
            'rsi': row['rsi'], 'OBV': row['OBV'],
            'retorno_log': row['retorno_log'], 'volatilidade': row['volatilidade'],
            'volume': row['volume'], 'volume_global': row['volume_global']
        })

        id_agg = obter_id(conn, 'dim_agregados', {
            'hora_num': row['hora_num'], 'minuto': row['minuto'],
            'fechamento_dia_anterior': row['fechamento_dia_anterior'],
            'volume_dia_anterior': row['volume_dia_anterior'],
            'maximo_dia_anterior': row['maximo_dia_anterior'],
            'minimo_dia_anterior': row['minimo_dia_anterior']
        })

        valores_fato = (
            row['abertura'], row['minimo'], row['maximo'], row['fechamento'],
            row['abertura'], row['minimo_global'], row['maximo_global'], row['fechamento_global'],
            id_tempo, id_ind, id_agg
        )

        conn.execute("""
            INSERT OR IGNORE INTO fato_precos (
                abertura, minima, maxima, fechamento,
                abertura_global, minima_global, maxima_global, fechamento_global,
                id_tempo, id_indicadores, id_agregados
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, valores_fato)

        novos_registros += 1

    conn.commit()
    conn.close()
    print(f"Carga concluída com {novos_registros} novos registros.")

