# PI de Previsão de Ações
Esta API permite prever preços de ações com base em dados históricos do Yahoo Finance. São disponibilizadas rotas para previsão individual, múltipla (batch), e listagem de modelos salvos.

# Rotas Disponíveis

### GET /

Executa previsão para 5 tickers pré-definidos (AAPL, MSFT, GOOGL, META, TSLA).

Exemplo de uso com curl:

curl http://localhost:8000/
POST /forecast

Executa previsão de uma única ação com base nos dados enviados no corpo da requisição.

Corpo esperado:

```json
{
  "ticker": "AAPL",
  "start_date": "2020-01-01",
  "end_date": "2023-01-01",
  "window_size": 60,
  "epochs": 10,
  "batch_size": 32
}
```

### Exemplo com curl:

```bash
curl -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "start_date": "2020-01-01",
    "end_date": "2023-01-01",
    "window_size": 60,
    "epochs": 10,
    "batch_size": 32
  }'
```

### GET /forecast/batch/{count}

Executa previsão para múltiplos tickers (até o número informado em count). Os tickers estão definidos internamente.


Exemplo com curl (para os 10 primeiros tickers):

```bash
curl "http://localhost:8000/forecast/batch/10?start_date=2020-01-01&end_date=2023-01-01&window_size=60&epochs=5&batch_size=32"
```

### GET /tickers

Retorna a lista de tickers com modelos previamente salvos.

```bash
curl http://localhost:8000/tickers
```

### >> Observações <<
O treinamento do modelo pode ser demorado dependendo do número de épocas (epochs) e da quantidade de dados.

A API salva os modelos treinados em saved_models/ e reutiliza-os quando disponíveis.

Requisições em lote (batch) possuem um sleep(3) entre execuções para evitar bloqueios da API do Yahoo Finance.