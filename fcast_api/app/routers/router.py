from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.etl import extract_stock_data
from app.model.forecast import (
    prepare_data, build_model,
    save_model, load_existing_model,
    get_model_filename
)
from app.metrics.evaluate import evaluate
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from time import sleep
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

WINDOW_SIZE_DEFAULT = 40
EPOCHS_DEFAULT = 100
BATCH_SIZE_DEFAULT = 32

class ForecastRequest(BaseModel):
    ticker: str
    start_date: str = (datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d")
    end_date: str
    window_size: int = WINDOW_SIZE_DEFAULT
    epochs: int = EPOCHS_DEFAULT
    batch_size: int = BATCH_SIZE_DEFAULT

@router.get("/")
async def root_forecast():
    tickers = ["AAPL", "MSFT"]
    start_date: str = (datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")
    window_size = WINDOW_SIZE_DEFAULT
    epochs = EPOCHS_DEFAULT
    batch_size = 32

    results = []

    for ticker in tickers:
        try:
            df = extract_stock_data(ticker, start_date, end_date)
            X, y, scaler = prepare_data(df, window_size)

            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]

            model_file = get_model_filename(ticker, window_size)
            if os.path.exists(model_file):
                model = load_existing_model(model_file)
            else:
                model = build_model((X.shape[1], X.shape[2]))
                model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=0)
                save_model(model, model_file)

            y_pred = model.predict(X_test)
            y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten().tolist()
            y_pred_rescaled = scaler.inverse_transform(y_pred).flatten().tolist()

            metrics = evaluate(y_test_rescaled, y_pred_rescaled)

            results.append({
                "ticker": ticker,
                "status": "success",
                "model": {
                    "path": model_file,
                    "window_size": window_size
                },
                "prediction_summary": {
                    "last_real_value": y_test_rescaled[-1] if y_test_rescaled else None,
                    "last_predicted_value": y_pred_rescaled[-1] if y_pred_rescaled else None,
                    "metrics": metrics
                },
                "forecast_series": {
                    "real_values": y_test_rescaled,
                    "predicted_values": y_pred_rescaled
                }
            })
        except Exception as e:
            results.append({
                "ticker": ticker,
                "status": "error",
                "message": f"Falha ao processar '{ticker}': {str(e)}"
            })

    return {"results": results}

@router.post("/forecast")
async def forecast(request: ForecastRequest):
    try:
        df = extract_stock_data(request.ticker, request.start_date, request.end_date)
        X, y, scaler = prepare_data(df, request.window_size)

        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        model_file = get_model_filename(request.ticker, request.window_size)

        if os.path.exists(model_file):
            model = load_existing_model(model_file)
        else:
            model = build_model((X.shape[1], X.shape[2]))
            model.fit(X_train, y_train, epochs=request.epochs, batch_size=request.batch_size, validation_split=0.1, verbose=0)
            save_model(model, model_file)

        y_pred = model.predict(X_test)
        y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten().tolist()
        y_pred_rescaled = scaler.inverse_transform(y_pred).flatten().tolist()

        metrics = evaluate(y_test_rescaled, y_pred_rescaled)

        return {
            "ticker": request.ticker,
            "status": "success",
            "model": {
                "path": model_file,
                "window_size": request.window_size
            },
            "prediction_summary": {
                "last_real_value": y_test_rescaled[-1] if y_test_rescaled else None,
                "last_predicted_value": y_pred_rescaled[-1] if y_pred_rescaled else None,
                "metrics": metrics
            },
            "forecast_series": {
                "real_values": y_test_rescaled,
                "predicted_values": y_pred_rescaled
            }
        }
    except Exception as e:
        return {
            "ticker": request.ticker,
            "status": "error",
            "message": f"Falha ao processar '{request.ticker}': {str(e)}"
        }

@router.get("/tickers")
async def list_saved_tickers():
    files = os.listdir("saved_models")
    tickers = set()

    for f in files:
        if f.endswith(".keras"):
            parts = f.split("_")
            ticker = parts[0].upper()
            tickers.add(ticker)

    return JSONResponse(content={"available_tickers": sorted(tickers)})

@router.get("/forecast/batch/{count}")
async def forecast_batch(
    count: int = 5,
    start_date: str = (datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d"),
    end_date: str = datetime.today().strftime("%Y-%m-%d"),
    window_size: int = WINDOW_SIZE_DEFAULT,
    epochs: int = EPOCHS_DEFAULT,
    batch_size: int = 32
):
    logging.info(f"Batch forecast params: {count}, {start_date}, {end_date}, {window_size}, {epochs}, {batch_size}")
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "JNJ", "V",
        "PG", "UNH", "HD", "MA", "BAC", "XOM", "PFE", "DIS", "KO", "INTC",
        "NFLX", "PEP", "MRK", "ABBV", "CSCO", "ADBE", "CRM", "T", "WMT", "NKE",
        "ORCL", "VZ", "MCD", "CVX", "ABT", "LLY", "QCOM", "TXN", "NEE", "MDT",
        "COST", "DHR", "AMGN", "BMY", "AVGO", "ACN", "UNP", "HON", "IBM", "PM",
        "LOW", "LIN", "UPS", "INTU", "SBUX", "GE", "RTX", "CAT", "LMT", "GILD",
        "DE", "ISRG", "NOW", "SPGI", "TMO", "EL", "ZTS", "BLK", "ADI", "PLD",
        "MU", "MO", "SYK", "CI", "BDX", "CHTR", "MMC", "SO", "PNC", "FISV",
        "USB", "CB", "ICE", "MDLZ", "C", "ADP", "DUK", "GM", "REGN", "EW",
        "AXP", "VRTX", "SHW", "APD", "TGT", "CL", "ETN", "EMR", "HUM", "ECL"
    ]

    results = []

    for ticker in tickers[:count]:
        sleep(3)
        try:
            df = extract_stock_data(ticker, start_date, end_date)
            X, y, scaler = prepare_data(df, window_size)

            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]

            model_file = get_model_filename(ticker, window_size)
            if os.path.exists(model_file):
                logging.info(f"Loading existing model for {ticker} from {model_file}")
                model = load_existing_model(model_file)
            else:
                model = build_model((X.shape[1], X.shape[2]))
                model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0)
                save_model(model, model_file)

            logging.info(f"Predicting with model for {ticker}")
            y_pred = model.predict(X_test)
            y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten().tolist()
            y_pred_rescaled = scaler.inverse_transform(y_pred).flatten().tolist()

            logging.info(f"Evaluating predictions for {ticker}")
            metrics = evaluate(y_test_rescaled, y_pred_rescaled)
            logging.info(f"Forecast completed for {ticker}")
            results.append({
                "ticker": ticker,
                "status": "success",
                "model": {
                    "path": model_file,
                    "window_size": window_size
                },
                "prediction_summary": {
                    "last_real_value": y_test_rescaled[-1] if y_test_rescaled else None,
                    "last_predicted_value": y_pred_rescaled[-1] if y_pred_rescaled else None,
                    "metrics": metrics
                },
                "forecast_series": {
                    "real_values": y_test_rescaled,
                    "predicted_values": y_pred_rescaled
                }
            })
        except Exception as e:
            results.append({
                "ticker": ticker,
                "status": "error",
                "message": f"Falha ao processar '{ticker}': {str(e)}"
            })

    return {"results": results}