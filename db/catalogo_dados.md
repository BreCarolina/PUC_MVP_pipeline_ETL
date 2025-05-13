
# 📚 Catálogo de Dados — Banco Dimensional de Ativos da B3

Este catálogo descreve o esquema de banco de dados utilizado no pipeline de ETL de ativos da B3. O modelo segue a estrutura de **modelo estrela**, com três tabelas dimensionais e uma tabela fato.

---

## 🧱 Tabela: `dim_tempo`

| Coluna         | Tipo     | Descrição                                      |
|----------------|----------|-----------------------------------------------|
| `id_tempo`     | INTEGER  | Chave primária (autoincremento)               |
| `data`         | TEXT     | Data no formato `YYYY-MM-DD`                  |
| `hora`         | TEXT     | Hora no formato `HH:MM:SS`                    |
| `dia_da_semana`| INTEGER  | Dia da semana (`0=segunda`, ..., `6=domingo`) |
| 🔒 **Unique**  | (`data`, `hora`) — evita duplicação                      |

---

## 📊 Tabela: `dim_indicadores`

| Coluna            | Tipo     | Descrição                                             |
|-------------------|----------|--------------------------------------------------------|
| `id_indicadores`  | INTEGER  | Chave primária (autoincremento)                        |
| `SMA_10`          | REAL     | Média móvel simples de 10 períodos                     |
| `EMA_10`          | REAL     | Média móvel exponencial de 10 períodos                |
| `MACD`            | REAL     | Indicador de convergência/divergência de médias       |
| `Signal_Line`     | REAL     | Linha de sinal do MACD                                |
| `rsi`             | REAL     | Índice de força relativa                              |
| `OBV`             | REAL     | On-Balance Volume                                     |
| `retorno_log`     | REAL     | Logaritmo do retorno entre períodos                   |
| `volatilidade`    | REAL     | Volatilidade calculada                                |
| `volume`          | INTEGER  | Volume negociado no período                           |
| `volume_global`   | INTEGER  | Volume total agregado até o momento                   |
| 🔒 **Unique**     | Todas as colunas — evita duplicidade nos indicadores              |

---

## 📈 Tabela: `dim_agregados`

| Coluna                  | Tipo     | Descrição                                         |
|-------------------------|----------|--------------------------------------------------|
| `id_agregados`          | INTEGER  | Chave primária (autoincremento)                 |
| `hora_num`              | INTEGER  | Hora convertida para valor numérico (ex: 10h30 = 1030) |
| `minuto`                | INTEGER  | Minuto do registro                              |
| `fechamento_dia_anterior` | REAL   | Preço de fechamento do dia anterior             |
| `volume_dia_anterior`   | INTEGER  | Volume total do dia anterior                    |
| `maximo_dia_anterior`   | REAL     | Preço máximo do dia anterior                    |
| `minimo_dia_anterior`   | REAL     | Preço mínimo do dia anterior                    |
| 🔒 **Unique**           | Todas as colunas — evita duplicação de agregados           |

---

## 📦 Tabela: `fato_precos`

| Coluna             | Tipo     | Descrição                                      |
|--------------------|----------|-----------------------------------------------|
| `id`               | INTEGER  | Chave primária (autoincremento)               |
| `abertura`         | REAL     | Preço de abertura no período                  |
| `minima`           | REAL     | Preço mínimo no período                       |
| `maxima`           | REAL     | Preço máximo no período                       |
| `fechamento`       | REAL     | Preço de fechamento no período                |
| `abertura_global`  | REAL     | Preço de abertura ajustado/global             |
| `minima_global`    | REAL     | Mínima global acumulada                       |
| `maxima_global`    | REAL     | Máxima global acumulada                       |
| `fechamento_global`| REAL     | Fechamento global acumulado                   |
| `id_tempo`         | INTEGER  | FK para `dim_tempo`                           |
| `id_indicadores`   | INTEGER  | FK para `dim_indicadores`                     |
| `id_agregados`     | INTEGER  | FK para `dim_agregados`                       |
| 🔒 **Unique**       | (`id_tempo`, `id_indicadores`, `id_agregados`) — evita duplicação de fatos |

---

## 🔗 Relacionamentos

- `fato_precos.id_tempo` → `dim_tempo.id_tempo`
- `fato_precos.id_indicadores` → `dim_indicadores.id_indicadores`
- `fato_precos.id_agregados` → `dim_agregados.id_agregados`
