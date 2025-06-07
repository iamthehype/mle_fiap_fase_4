# 📈 LSTM Stock Forecasting API

Este projeto fornece uma API desenvolvida com **FastAPI** para previsão de preços de ações com base em dados históricos. Utiliza redes neurais LSTM implementadas com **TensorFlow**, processamento de dados com **Polars**, e normalização via **scikit-learn**.

## 🚀 Funcionalidades

- 🔮 Previsão de preços de ações usando LSTM
- 🔁 Treinamento automático e reutilização de modelos salvos
- ⚖️ Normalização de dados com janela deslizante
- 📊 Avaliação com métricas de regressão
- 🌐 API REST com rotas de previsão individual e em lote

## 📂 Estrutura do Projeto

```
mle_fiap_fase_4/
├── app/
│   ├── model/
│   │   └── forecast.py
│   ├── routes/
│   │   └── router.py
│   ├── utils/
│   │   └── etl.py
│   ├── metrics/
│   │   └── evaluate.py
│   └── main.py
├── saved_models/
└── README.md
```

## ⚙️ Configuração e Execução

### 1. Instalação das dependências

```bash
pip install -r requirements.txt
```

### 2. Rodando o servidor

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: http://localhost:8000

## 📥 Exemplo de Requisição (POST /forecast)

```http
POST /forecast
Content-Type: application/json
```

```json
{
  "ticker": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "window_size": 60,
  "epochs": 100,
  "batch_size": 32
}
```

### 🟢 Exemplo de Resposta

```json
{
  "ticker": "AAPL",
  "status": "success",
  "model": {
    "path": "saved_models/aapl_ws60.keras",
    "window_size": 60
  },
  "prediction_summary": {
    "last_real_value": 182.12,
    "last_predicted_value": 181.34,
    "metrics": {
      "MAE": 1.23,
      "MSE": 2.45,
      "RMSE": 1.56,
      "R2": 0.93
    }
  },
  "forecast_series": {
    "real_values": [...],
    "predicted_values": [...]
  }
}
```

## 🔀 Endpoints Disponíveis

| Método | Rota                        | Descrição                                         |
|--------|-----------------------------|---------------------------------------------------|
| GET    | `/`                         | Previsão padrão para `AAPL` e `MSFT`              |
| POST   | `/forecast`                | Previsão customizada para um ticker específico    |
| GET    | `/tickers`                 | Lista de modelos salvos no diretório local        |
| GET    | `/forecast/batch/{count}`  | Executa previsões em lote para múltiplos tickers  |

## 📊 Arquitetura do Modelo

```python
LSTM(100) → BatchNormalization → Dropout(0.2)
→ LSTM(100) → BatchNormalization → Dropout(0.2)
→ LSTM(50)
→ Dense(20, activation='relu')
→ Dense(1)
```

## 📈 Métricas de Avaliação

- MAE: Mean Absolute Error
- MSE: Mean Squared Error
- RMSE: Root Mean Squared Error
- R²: Coeficiente de Determinação

## 🧠 Estratégia de Treinamento

- Split 80/20 para treino/teste
- Normalização com MinMaxScaler
- Validação: 10%
- Persistência automática do modelo `.keras` por ticker

## 🗃️ Persistência

Os modelos são salvos no formato:

```
saved_models/{ticker}_ws{window_size}.keras
```

Na próxima requisição com os mesmos parâmetros, o modelo é carregado ao invés de ser refeito.

## 📌 Requisitos

```text
fastapi
polars
numpy
scikit-learn
tensorflow
pydantic
```

> Obs.: o uso de GPU é desabilitado via `os.environ["CUDA_VISIBLE_DEVICES"] = "-1"` por padrão.

## 📜 Licença

Este projeto está licenciado sob a licença MIT.

## 🤝 Contribuições

Contribuições são bem-vindas! Abra uma issue ou envie um pull request.
