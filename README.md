# Pipeline de Extração e Processamento de Dados de Ativos da B3

Este projeto realiza a **extração, limpeza, transformação e carga incremental** de dados financeiros de ativos da B3 (ex: `PETR4`, `BBDC4`, `LREN3`), estruturando-os em um banco de dados dimensional com modelo estrela.

O objetivo final é utilizar esses dados como base de estudo para **compra e venda de ativos**, além de permitir o desenvolvimento de **modelos preditivos**, especialmente modelos **LSTM (Long Short-Term Memory)** voltados à previsão de preços e comportamentos do mercado intradiário.

> **Licença:** Este projeto é disponibilizado sob uma licença personalizada de uso restrito. Consulte a seção **Licença** ao final deste documento para mais detalhes.

---

## 🖥️ Ambiente de Execução

O projeto foi concebido para execução no **Google Colab**, aproveitando a estrutura de diretórios padrão `/content/`.

### Estrutura de Pastas

Monte corretamente a árvore de diretórios `MVP_pipeline/`:

```python
!mkdir -p MVP_pipeline
%cd MVP_pipeline
!mkdir -p src/pipeline
!mkdir -p data/raw
!mkdir -p data/cleaned
!mkdir -p data/transformed
!mkdir -p db
!mkdir -p reports
!mkdir -p docs
```

### Variáveis de Ambiente

Configure variáveis sensíveis em um arquivo `.env` usando `python-dotenv`.

---

## 📁 Controle de Versão

Utilize Git para versionamento. Clone o repositório:

```bash
!git clone https://github.com/seu_usuario/seu_repositorio.git
%cd seu_repositorio
```

Registre alterações com:

```bash
!git add .
!git commit -m "[ETAPA] Mensagem descritiva da mudança"
!git push origin main
```

> Use um `.gitignore` para ignorar arquivos grandes e temporários, como `.csv` intermediários.

---

## 🔄 Etapas do Pipeline

### 1. Extração e Limpeza (`extracao_dados.py`)

- Download de dados intradiários via `yfinance`
- Extração incremental de novos dados
- Conversão para fuso BRT
- Padronização de nomes e colunas
- Filtragem de duplicatas e dados nulos
- Manutenção de dias úteis e horários do pregão (09:55 - 18:05)
- Logs informativos
- Salva em: `data/raw/` e `data/cleaned/`

---

### 2. Transformação (`transformacao_dados.py`)

- Incrementa apenas registros novos
- Ordena cronologicamente
- Calcula indicadores técnicos:
  - Médias móveis (SMA, EMA)
  - MACD e sinal
  - RSI
  - OBV
  - Log-retorno e volatilidade
- Adiciona atributos temporais:
  - `dia_da_semana`, `hora_num`, `minuto`
- Adiciona estatísticas diárias (atuais e anteriores)
- Preenche nulos técnicos com médias
- Salva em: `data/transformed/`

---

### 3. Carga Dimensional (`carga_dados.py`)

- Conecta ao SQLite: `modelagem/database/`
- Criação automática das tabelas:
  - `dim_tempo`, `dim_indicadores`, `dim_agregados`
  - `fato_precos`
- Carga incremental com verificação de unicidade
- Uso de `INSERT OR IGNORE`
- Integridade via chaves estrangeiras
- Logs de inserções realizadas

---

## 📦 Requisitos

- Python **3.10+**

### Bibliotecas

- `pandas`, `numpy`, `yfinance`
- `matplotlib`, `seaborn`
- `sqlite3`, `sqlalchemy`
- `python-dotenv`, `gitpython`
- `datetime`, `os`, `logging`

### Instalação

```bash
!pip install -r requirements.txt
```

---

## ⚙️ Execução

### Pipeline Empacotado

O projeto inclui um executável `.exe` para rodar o pipeline sem necessidade de Python instalado.

### Passos

1. **Download e extração** do zip contendo o `.exe`
2. **Configuração do `.env`**:

Exemplo:
```env
TICKER='LREN3.SA'
PATH_PROJETO='C:\caminho\para\seu\projeto\MVP_pipeline'
INTERVALO='5m'
```

3. **Executar o arquivo `.exe`**

- O pipeline irá:
  - Criar pastas automaticamente
  - Processar os dados com base no `.env`
  - Gerar logs em `log_pipeline.log`

---

## 📊 Verificando os Resultados

- **Logs:** `log_pipeline.log`
- **Dados:** `data/raw/`, `data/cleaned/`, `data/transformed/`

---

## 💡 Observações

- Compatível com qualquer ticker B3 aceito pelo Yahoo Finance (ex: `PETR4.SA`, `BBDC4.SA`, `LREN3.SA`)
- Extração incremental evita retrabalho
- Logs detalhados para facilitar depuração

---

## 📄 Licença

Projeto distribuído sob **licença de uso restrito**. A redistribuição, comercialização ou adaptação só é permitida com autorização expressa do autor.

---

Desenvolvido com foco em automação, escalabilidade e aplicabilidade em ciência de dados financeiros.