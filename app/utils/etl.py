from datetime import datetime, timedelta
import yfinance as yf
import polars as pl
import pandas as pd
import os
import time
import logging

def yfinance_is_working(ticker="AAPL") -> bool:
    try:
        df = yf.download(ticker, period="5d", progress=False)
        if df.empty:
            
            logging.error(f"YFinance não está funcionando corretamente para o ticker {ticker}.")
            return False
        return True
    except Exception:
        return False

def extract_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    max_retries: int = 5,
    delay: int = 5
) -> pl.DataFrame:
    logging.info(f"request params: {ticker}, {start_date}, {end_date}, {max_retries}, {delay}")

    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)

            if df.empty:
                raise ValueError(f"Nenhum dado encontrado para o ticker '{ticker}' no período informado.")

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            if 'Close' not in df.columns:
                raise ValueError(f"Coluna 'Close' não encontrada após normalização.")

            df = df[['Close']].dropna()
            df.reset_index(inplace=True) 
            df.columns = ['date', 'price']
            return pl.DataFrame(df)

        except Exception as e:
            logging.error(f"[{attempt}/{max_retries}] Falha ao extrair dados para '{ticker}': {e}")
            if attempt < max_retries:
                time.sleep(delay * attempt)
            else:
                raise e