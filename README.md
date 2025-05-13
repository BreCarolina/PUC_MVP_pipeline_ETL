
# Pipeline de Extração e processamento de Dados de Ativos da B3

Este projeto realiza a extração, limpeza, transformação e carga incremental de dados financeiros de ativos da B3
(ex: PETR4, BBDC4, LREN3), estruturando-os em um banco de dados dimensional com modelo estrela.

O objetivo final é utilizar esses dados como base de estudo para compra e venda de ativos. Além disso, o material preparado poderá ser utilizado
para desenvolvimento de modelos preditivos, especialmente modelos LSTM (Long Short-Term Memory), voltados à previsão de preços e comportamentos do mercado intradiário.

Este projeto é disponibilizado sob uma licença personalizada de uso restrito.
Consulte a seção "Licença" ao final deste documento para mais detalhes.

Ambiente de Execução

O projeto foi concebido para execução em ambiente Google Colab, aproveitando a estrutura de diretórios padrão /content/.

Certifique-se de montar corretamente a árvore de pastas (MVP_pipeline/) dentro do ambiente Colab.

Variáveis de ambiente sensíveis devem ser configuradas via .env (utilizando python-dotenv).

Código rápido para criar a estrutura de diretórios:

"""

!mkdir -p MVP_pipeline

%cd MVP_pipeline

!mkdir -p src/pipeline

!mkdir -p data/raw

!mkdir -p data/cleaned

!mkdir -p data/transformed

!mkdir -p db

!mkdir -p reports

!mkdir -p docs

"""

Controle de Versão

O projeto utiliza controle de versão com Git. Recomenda-se clonar o repositório e manter os commits organizados por etapa do pipeline:

!git clone https://github.com/seu_usuario/seu_repositorio.git
%cd seu_repositorio

Para registrar alterações:

!git add .
!git commit -m "[ETAPA] Mensagem descritiva da mudança"
!git push origin main

Certifique-se de manter a estrutura de pastas conforme estabelecido no ambiente Colab e de versionar apenas arquivos relevantes (
utilize um .gitignore para ignorar bancos e arquivos grandes temporários, como os .csv intermediários).

Etapas do Pipeline

1. Extração e Limpeza (extracao_dados.py)

Realiza download de dados intradiários do Yahoo Finance com yfinance, adaptando o período conforme o horário atual e se é dia úil.

Verifica se já existem dados limpos anteriores e extrai apenas novos dados, evitando reprocessamento completo.

Converte o índice de tempo para o fuso horário de São Paulo (BRT), remove timezone e extrai as colunas data e hora.

Renomeia colunas para padronização (abertura, minimo, maximo, fechamento, volume).

Filtra duplicatas e registros com mais de 50% de valores nulos.

Mantém apenas dias úteis e horários dentro do pregão (entre 09:55 e 18:05).

Ordena os dados por data e hora.

Os dados são salvos incrementalmente nas pastas data/raw/ e data/cleaned/.

Exibe logs informativos durante cada etapa do processo.

2. Transformação (transformacao_dados.py)

Carrega os dados limpos e incrementa apenas registros ainda não processados.

Ordena por data e hora.

Calcula indicadores técnicos:

Médias móveis (SMA, EMA)

MACD e linha de sinal

RSI

OBV (On-Balance Volume)

Log-retorno e volatilidade

Adiciona atributos temporais:

dia_da_semana, hora_num, minuto

Adiciona estatísticas diárias (atuais e do dia anterior):

Fechamento, volume, máximo, mínimo

Preenche nulos técnicos com a média da respectiva coluna.

Salva em data/transformed/.



3. Carga Dimensional (carga_dados.py)

Lê os dados transformados e conecta-se ao banco SQLite (modelagem/database/).

Garante a criação das tabelas dimensionais e fato, caso não existam:

dim_tempo: data, hora, dia_da_semana

dim_indicadores: indicadores técnicos e volume

dim_agregados: horário numérico e estatísticas do dia anterior

fato_precos: preços com chaves estrangeiras para as três dimensões

Para cada linha do CSV transformado:

Verifica se o par (data, hora) já está presente em dim_tempo.

Se não estiver, insere os dados em suas respectivas dimensões utilizando verificação de unicidade e retorna os id_* associados.

Insere os valores na tabela fato apenas se a combinação (id_tempo, id_indicadores, id_agregados) ainda não existir, utilizando INSERT OR IGNORE.

Operações chave:

Carga incremental e segura (evita duplicação).

Chaves estrangeiras asseguram integridade entre fato e dimensões.

Caminhos e arquivos são montados dinamicamente com base no ticker e estrutura do projeto.

Exibe o número total de novos registros adicionados ao final da execução.

Requisitos

Python 3.10+

Bibliotecas utilizadas no pipeline:

pandas, numpy, yfinance, matplotlib, seaborn

sqlite3, sqlalchemy

python-dotenv, gitpython

datetime, os, logging

Instalação:

!pip install -r requirements.txt

Execução

Pipeline completo para um ativo:

Este projeto foi empacotado para que o cliente possa rodar sem a necessidade de ter Python instalado. O pacote inclui um arquivo executável .exe, que é responsável por rodar o pipeline automaticamente.

1. Download e Descompactação do Arquivo

Faça o download do arquivo zipado que contém o executável e todos os arquivos necessários. Após o download, extraia o conteúdo para um diretório de sua escolha.

2. Configuração do Arquivo .env

Dentro do diretório extraído, você encontrará o arquivo .env, onde é necessário configurar as variáveis de ambiente:

TICKER: O ticker do ativo a ser processado (ex: 'LREN3.SA').

PATH_PROJETO: O caminho base onde o projeto está localizado.

INTERVALO: O intervalo de coleta de dados (ex: '5m', '15m', '1h').

Exemplo de como criar o arquivo .env


TICKER='LREN3.SA' 
PATH_PROJETO='C:\\caminho\\para\\seu\\projeto\\MVP_pipeline' 
INTERVALO='5m'


3. Executando o Pipeline

Após ajustar o arquivo .env, basta executar o arquivo ``.

O processo irá ler os parâmetros do arquivo .env e iniciar a execução do pipeline.

As pastas necessárias (data/raw, data/cleaned, data/transformed, db) serão criadas automaticamente, caso ainda não existam.

O pipeline irá baixar, processar e armazenar os dados de acordo com o ticker e intervalo definidos.

Logs serão gerados em log_pipeline.log.

4. Verificando os Resultados

Logs: O arquivo log_pipeline.log conterá informações sobre a execução, erros e sucessos.

Dados: Os dados processados serão armazenados nas pastas data/raw/, data/cleaned/ e data/transformed/.



Observações

O pipeline é genérico e funciona para qualquer ticker da B3 aceito pelo Yahoo Finance (ex: PETR4.SA, BBDC4.SA, LREN3.SA).

A extração é incremental: evita retrabalho e reprocessamentos desnecessários.

O sistema realiza logs detalhados para facilitar o acompanhamento da execução e depuração.


