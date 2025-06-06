## Exemplos de uso
## Endpoint /forecast

```bash
curl -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "start_date": "2022-01-01",
    "end_date": "2023-01-01",
    "window_size": 60,
    "epochs": 100,
    "batch_size": 32
  }'
```

## Os paramentros window_size, epochs e batch_size nao sao obrigatorios
## A requisicao pode ser feita da seguinte maneira

```bash
curl -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "start_date": "2022-01-01",
    "end_date": "2025-06-04"
  }'
```